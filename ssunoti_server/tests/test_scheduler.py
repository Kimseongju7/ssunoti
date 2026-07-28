"""APScheduler 기반 스케줄러 (scheduler.py) 단위 테스트.

실제 스케줄러를 기동(start())하지 않고 잡 등록 및 트리거 설정값을 검증한다.
실제 SSUPath 요청·Firestore 쓰기·FCM 발송은 모두 fake 로 대체한다.

검증 항목:
(a) 등록된 잡이 정확히 2개이고 ID 가 일치한다.
(b) 신규 수집 잡: IntervalTrigger, 60분 이상.
(c) 원시값 갱신 잡: IntervalTrigger, 15분.
(e) 모든 잡의 max_instances == 1.
(f) 각 잡 함수를 직접 호출하면 INFO 로그가 1회 이상 기록된다.
(g) 세션이 만료되면 crawler.login() 이 호출된다.
(h) 세션이 유효하면 crawler.login() 이 호출되지 않는다.
(i) 초기 적재 진입점 run_backfill() 은 backfill=True 로 위임하며 주기 잡이 아니다.

마감 전용 잡(cron 매일 09:00)은 15분 잡과 동작이 완전히 같아 제거되었다.
`deadline` 필드는 원시값 갱신 잡이 15분마다 함께 갱신한다.
"""
from __future__ import annotations

import logging

import pytest

from ssunoti.scheduler import (
    COLLECT_INTERVAL_MINUTES,
    UPDATE_INTERVAL_MINUTES,
    NoticeScheduler,
)


# ── Fake 객체 ──────────────────────────────────────────────────────────────────


class FakeCrawler:
    """실제 네트워크 요청을 하지 않는 크롤러 대체."""

    def __init__(self, session_valid: bool = True) -> None:
        self.session_valid = session_valid
        self.login_calls: int = 0
        self.get_all_notices_calls: int = 0

    def is_session_valid(self) -> bool:
        return self.session_valid

    def login(self) -> bool:
        self.login_calls += 1
        return True

    def get_all_notices(self, year: int | None = None, status: str = "RS02") -> list:
        self.get_all_notices_calls += 1
        return []


class FakeNotifier:
    """FCM 발송을 하지 않는 알리미 대체."""

    def __init__(self) -> None:
        self.process_calls: int = 0
        self.backfill_flags: list[bool] = []

    def process_new_notices(self, notices: list, *, backfill: bool = False) -> int:
        self.process_calls += 1
        self.backfill_flags.append(backfill)
        return len(notices)


class FakeStore:
    """Firestore 쓰기를 하지 않는 저장소 대체."""

    def __init__(self) -> None:
        self.upsert_many_calls: int = 0

    def upsert_many(self, notices: list) -> None:
        self.upsert_many_calls += 1


# ── pytest fixtures ───────────────────────────────────────────────────────────


@pytest.fixture()
def fake_crawler() -> FakeCrawler:
    return FakeCrawler(session_valid=True)


@pytest.fixture()
def fake_notifier() -> FakeNotifier:
    return FakeNotifier()


@pytest.fixture()
def fake_store() -> FakeStore:
    return FakeStore()


@pytest.fixture()
def notice_scheduler(
    fake_crawler: FakeCrawler,
    fake_notifier: FakeNotifier,
    fake_store: FakeStore,
) -> NoticeScheduler:
    return NoticeScheduler(fake_crawler, fake_notifier, fake_store)


@pytest.fixture()
def registered_scheduler(notice_scheduler: NoticeScheduler):
    """잡이 등록된 BackgroundScheduler. start() 는 호출하지 않는다."""
    from apscheduler.schedulers.background import BackgroundScheduler

    sched = BackgroundScheduler()
    notice_scheduler.setup(sched)
    return sched


# ── (a) 잡 개수·ID 검증 ────────────────────────────────────────────────────────


class TestJobRegistration:
    """스케줄러 잡 등록 검증 (실제 기동 없음)."""

    def test_exactly_two_jobs_registered(
        self, registered_scheduler
    ) -> None:
        """등록된 잡이 정확히 2개여야 한다."""
        assert len(registered_scheduler.get_jobs()) == 2

    def test_job_ids_present(self, registered_scheduler) -> None:
        """두 가지 잡 ID 가 모두 존재해야 한다."""
        job_ids = {job.id for job in registered_scheduler.get_jobs()}
        assert job_ids == {"collect_new_notices", "update_notices"}

    def test_no_separate_deadline_job(self, registered_scheduler) -> None:
        """마감 전용 잡은 등록되지 않는다.

        15분 잡이 deadline 을 포함한 원시값 전부를 갱신하므로,
        별도의 cron 잡은 같은 크롤링을 한 번 더 하는 것 외에 하는 일이 없었다.
        """
        job_ids = {job.id for job in registered_scheduler.get_jobs()}
        assert "update_deadline" not in job_ids


# ── (b)(c) IntervalTrigger 검증 ────────────────────────────────────────────────


class TestIntervalTriggers:
    """IntervalTrigger 설정값 검증."""

    def test_collect_job_uses_interval_trigger(
        self, registered_scheduler
    ) -> None:
        """신규 수집 잡이 IntervalTrigger 를 사용한다."""
        from apscheduler.triggers.interval import IntervalTrigger

        job = registered_scheduler.get_job("collect_new_notices")
        assert isinstance(job.trigger, IntervalTrigger)

    def test_collect_job_interval_ge_60_min(
        self, registered_scheduler
    ) -> None:
        """신규 수집 잡의 주기가 60분 이상이어야 한다."""
        job = registered_scheduler.get_job("collect_new_notices")
        assert job.trigger.interval.total_seconds() >= COLLECT_INTERVAL_MINUTES * 60

    def test_update_job_uses_interval_trigger(
        self, registered_scheduler
    ) -> None:
        """원시값 갱신 잡이 IntervalTrigger 를 사용한다."""
        from apscheduler.triggers.interval import IntervalTrigger

        job = registered_scheduler.get_job("update_notices")
        assert isinstance(job.trigger, IntervalTrigger)

    def test_update_job_interval_is_15_min(
        self, registered_scheduler
    ) -> None:
        """원시값 갱신 잡의 주기가 정확히 15분이어야 한다."""
        job = registered_scheduler.get_job("update_notices")
        assert job.trigger.interval.total_seconds() == UPDATE_INTERVAL_MINUTES * 60


# ── (e) max_instances 검증 ─────────────────────────────────────────────────────


class TestMaxInstances:
    """모든 잡의 max_instances == 1 검증."""

    def test_all_jobs_max_instances_is_1(
        self, registered_scheduler
    ) -> None:
        """모든 잡의 max_instances 가 1이어야 한다."""
        for job in registered_scheduler.get_jobs():
            assert job.max_instances == 1, (
                f"잡 {job.id!r} 의 max_instances 가 1이 아닙니다: {job.max_instances}"
            )


# ── (f) 로그 기록 검증 ────────────────────────────────────────────────────────


class TestJobFunctionLogging:
    """각 잡 함수를 직접 호출했을 때 INFO 로그가 기록되는지 검증한다."""

    def test_collect_new_notices_emits_log(
        self, notice_scheduler: NoticeScheduler, caplog: pytest.LogCaptureFixture
    ) -> None:
        """collect_new_notices() 호출 시 최소 1건의 INFO 로그가 기록된다."""
        with caplog.at_level(logging.INFO, logger="ssunoti.scheduler"):
            notice_scheduler.collect_new_notices()
        assert len(caplog.records) >= 1

    def test_update_notices_emits_log(
        self, notice_scheduler: NoticeScheduler, caplog: pytest.LogCaptureFixture
    ) -> None:
        """update_notices() 호출 시 최소 1건의 INFO 로그가 기록된다."""
        with caplog.at_level(logging.INFO, logger="ssunoti.scheduler"):
            notice_scheduler.update_notices()
        assert len(caplog.records) >= 1


# ── (g)(h) 세션 만료·재로그인 검증 ─────────────────────────────────────────────


class TestSessionRelogin:
    """세션 만료 감지 시 재로그인이 호출되는지 검증한다."""

    def test_expired_session_triggers_login_in_collect(
        self, fake_notifier: FakeNotifier, fake_store: FakeStore
    ) -> None:
        """세션이 만료된 상태에서 collect_new_notices() 호출 시 login() 이 1회 호출된다."""
        crawler = FakeCrawler(session_valid=False)
        notice_scheduler = NoticeScheduler(crawler, fake_notifier, fake_store)
        notice_scheduler.collect_new_notices()
        assert crawler.login_calls == 1

    def test_valid_session_skips_login_in_collect(
        self, fake_notifier: FakeNotifier, fake_store: FakeStore
    ) -> None:
        """세션이 유효한 상태에서 collect_new_notices() 호출 시 login() 이 호출되지 않는다."""
        crawler = FakeCrawler(session_valid=True)
        notice_scheduler = NoticeScheduler(crawler, fake_notifier, fake_store)
        notice_scheduler.collect_new_notices()
        assert crawler.login_calls == 0

    def test_expired_session_triggers_login_in_update(
        self, fake_notifier: FakeNotifier, fake_store: FakeStore
    ) -> None:
        """세션이 만료된 상태에서 update_notices() 호출 시 login() 이 1회 호출된다."""
        crawler = FakeCrawler(session_valid=False)
        notice_scheduler = NoticeScheduler(crawler, fake_notifier, fake_store)
        notice_scheduler.update_notices()
        assert crawler.login_calls == 1


# ── (i) 초기 적재(backfill) 진입점 검증 ────────────────────────────────────────


class TestBackfillEntrypoint:
    """run_backfill() 이 backfill 모드로 위임하는지 검증한다.

    이 진입점이 없으면 빈 Firestore 로 처음 기동할 때 모집중 공고 전량이
    신규로 판정되어 전부 푸시가 나간다.
    """

    def test_run_backfill_delegates_with_backfill_true(
        self, notice_scheduler: NoticeScheduler, fake_notifier: FakeNotifier
    ) -> None:
        """run_backfill() 은 process_new_notices 를 backfill=True 로 1회 호출한다."""
        notice_scheduler.run_backfill()

        assert fake_notifier.process_calls == 1
        assert fake_notifier.backfill_flags == [True]

    def test_periodic_collect_does_not_use_backfill(
        self, notice_scheduler: NoticeScheduler, fake_notifier: FakeNotifier
    ) -> None:
        """주기 잡 collect_new_notices() 는 backfill=False 로 동작한다."""
        notice_scheduler.collect_new_notices()

        assert fake_notifier.backfill_flags == [False]

    def test_run_backfill_is_not_registered_as_a_job(
        self, registered_scheduler
    ) -> None:
        """초기 적재는 주기 잡이 아니다. 스케줄러에 등록되지 않는다."""
        job_ids = {job.id for job in registered_scheduler.get_jobs()}

        assert "run_backfill" not in job_ids
        assert len(job_ids) == 2

    def test_run_backfill_relogins_when_session_expired(
        self, fake_notifier: FakeNotifier, fake_store: FakeStore
    ) -> None:
        """세션이 만료된 상태에서 run_backfill() 호출 시 login() 이 1회 호출된다."""
        crawler = FakeCrawler(session_valid=False)
        notice_scheduler = NoticeScheduler(crawler, fake_notifier, fake_store)

        notice_scheduler.run_backfill()

        assert crawler.login_calls == 1

    def test_run_backfill_propagates_crawl_failure(
        self, fake_notifier: FakeNotifier, fake_store: FakeStore
    ) -> None:
        """초기 적재 실패는 삼키지 않고 전파한다.

        주기 잡과 달리 예외를 로그로만 남기면, 부분 적재 상태로 상주 실행에
        들어가 남은 공고가 전량 푸시된다.
        """

        class ExplodingCrawler(FakeCrawler):
            def get_all_notices(
                self, year: int | None = None, status: str = "RS02"
            ) -> list:
                raise RuntimeError("크롤링 실패")

        notice_scheduler = NoticeScheduler(
            ExplodingCrawler(session_valid=True), fake_notifier, fake_store
        )

        with pytest.raises(RuntimeError):
            notice_scheduler.run_backfill()

        assert fake_notifier.process_calls == 0
