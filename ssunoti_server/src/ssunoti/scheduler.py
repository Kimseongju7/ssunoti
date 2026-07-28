"""APScheduler 기반 상주 스케줄러.

세 개의 잡을 등록한다:
  - 신규 공고 수집: 60분 간격 (IntervalTrigger)
  - 정원 원시값 갱신: 15분 간격 (IntervalTrigger)
  - 마감 원시값 갱신: 매일 09:00 Asia/Seoul (CronTrigger)

모든 잡은 max_instances=1 로 중첩 실행을 막는다.
크롤러 세션이 만료되면 재로그인 후 작업을 이어간다.

크롤링 범위: 현재 연도 + status='RS02' (모집중) 만 수집한다.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# 잡 주기 상수 ─────────────────────────────────────────────────────────────────
COLLECT_INTERVAL_MINUTES: int = 60    # 신규 수집 최소 주기 (분)
CAPACITY_INTERVAL_MINUTES: int = 15   # 정원 갱신 주기 (분)
DEADLINE_CRON_HOUR: int = 9           # 마감 갱신 시각 (KST, 24시간)
DEADLINE_CRON_TIMEZONE: str = "Asia/Seoul"


class NoticeScheduler:
    """공고 수집·갱신 스케줄러.

    setup(scheduler) 로 apscheduler 인스턴스에 세 개의 잡을 등록한다.
    각 잡 함수는 독립적으로 호출할 수 있어 테스트가 용이하다.
    """

    def __init__(self, crawler: Any, notifier: Any, store: Any) -> None:
        """
        Args:
            crawler: SsupathCrawler 인스턴스 (또는 호환 가능한 fake).
            notifier: NoticeNotifier 인스턴스 (또는 호환 가능한 fake).
            store: NoticeStore 인스턴스 (또는 호환 가능한 fake).
        """
        self._crawler = crawler
        self._notifier = notifier
        self._store = store

    def _ensure_login(self) -> None:
        """세션이 만료되었으면 재로그인한다.

        crawler.is_session_valid() 가 False 를 반환하면 crawler.login() 을 호출한다.
        """
        if not self._crawler.is_session_valid():
            logger.info("세션 만료 감지 — 재로그인 시도")
            self._crawler.login()
            logger.info("재로그인 완료")

    def collect_new_notices(self) -> None:
        """신규 공고를 수집하고 FCM 알림을 발송한다 (interval 60분 이상).

        수집 범위: 현재 연도 + status='RS02' (모집중).
        신규 판정·FCM 발송·Firestore 쓰기는 NoticeNotifier 에 위임한다.
        """
        logger.info("신규 공고 수집 시작: %s", datetime.now().isoformat())
        try:
            self._ensure_login()
            year = datetime.now().year
            notices = self._crawler.get_all_notices(year=year, status="RS02")
            count = self._notifier.process_new_notices(notices)
            logger.info("신규 공고 수집 완료: %d건 처리", count)
        except Exception:
            logger.exception("신규 공고 수집 중 오류 발생")

    def update_capacity(self) -> None:
        """모집중 공고의 정원 원시값을 갱신한다 (interval 15분).

        신청자 수·대기자 수·모집 정원을 Firestore 에 upsert 한다.
        파생 상태는 저장하지 않는다.
        """
        logger.info("정원 원시값 갱신 시작: %s", datetime.now().isoformat())
        try:
            self._ensure_login()
            year = datetime.now().year
            notices = self._crawler.get_all_notices(year=year, status="RS02")
            self._store.upsert_many(notices)
            logger.info("정원 원시값 갱신 완료: %d건", len(notices))
        except Exception:
            logger.exception("정원 원시값 갱신 중 오류 발생")

    def update_deadline(self) -> None:
        """마감 원시값을 갱신한다 (cron 매일 09:00 Asia/Seoul).

        신청 마감 일시(application_period)를 Firestore 에 upsert 한다.
        임박 여부는 저장하지 않는다.
        """
        logger.info("마감 원시값 갱신 시작: %s", datetime.now().isoformat())
        try:
            self._ensure_login()
            year = datetime.now().year
            notices = self._crawler.get_all_notices(year=year, status="RS02")
            self._store.upsert_many(notices)
            logger.info("마감 원시값 갱신 완료: %d건", len(notices))
        except Exception:
            logger.exception("마감 원시값 갱신 중 오류 발생")

    def setup(self, scheduler: Any) -> None:
        """apscheduler 인스턴스에 세 개의 잡을 등록한다.

        Args:
            scheduler: apscheduler BackgroundScheduler (또는 호환 인스턴스).
                       이 메서드는 scheduler.start() 를 호출하지 않는다.
        """
        scheduler.add_job(
            self.collect_new_notices,
            trigger="interval",
            minutes=COLLECT_INTERVAL_MINUTES,
            max_instances=1,
            id="collect_new_notices",
            name="신규 공고 수집",
        )
        scheduler.add_job(
            self.update_capacity,
            trigger="interval",
            minutes=CAPACITY_INTERVAL_MINUTES,
            max_instances=1,
            id="update_capacity",
            name="정원 원시값 갱신",
        )
        scheduler.add_job(
            self.update_deadline,
            trigger="cron",
            hour=DEADLINE_CRON_HOUR,
            timezone=DEADLINE_CRON_TIMEZONE,
            max_instances=1,
            id="update_deadline",
            name="마감 원시값 갱신",
        )
