"""APScheduler 기반 상주 스케줄러.

두 개의 잡을 등록한다:
  - 신규 공고 수집: 60분 간격 (IntervalTrigger)
  - 원시값 갱신: 15분 간격 (IntervalTrigger)

원시값 갱신 잡 하나가 신청자·대기자·정원·마감을 모두 갱신한다.
별도의 마감 전용 잡(매일 09:00)을 두었더니 15분 잡과 완전히 같은 동작이어서
제거했다. 마감 시각은 `deadline` 필드로 15분마다 함께 갱신된다.

모든 잡은 max_instances=1 로 중첩 실행을 막는다.
크롤러 세션이 만료되면 재로그인 후 작업을 이어간다.

크롤링 범위: 현재 연도 + status='RS02' (모집중) 만 수집한다.
학교 서버 부하: 시간당 전수 페이지 순회 4회(15분 잡) + 1회(60분 잡).

초기 적재는 주기 잡이 아니다. run_backfill() 을 수동으로 1회 호출한다.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# 잡 주기 상수 ─────────────────────────────────────────────────────────────────
COLLECT_INTERVAL_MINUTES: int = 60   # 신규 수집 최소 주기 (분)
UPDATE_INTERVAL_MINUTES: int = 15    # 원시값 갱신 주기 (분)


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

    def update_notices(self) -> None:
        """모집중 공고의 원시값을 갱신한다 (interval 15분).

        신청자 수·대기자 수·모집 정원·마감 시각을 한 번에 Firestore 에 upsert 한다.
        네 값 모두 같은 크롤링 결과에서 나오므로 잡을 나눌 이유가 없다.
        파생 상태(임박 여부 등)는 저장하지 않는다.
        """
        logger.info("원시값 갱신 시작: %s", datetime.now().isoformat())
        try:
            self._ensure_login()
            year = datetime.now().year
            notices = self._crawler.get_all_notices(year=year, status="RS02")
            self._store.upsert_many(notices)
            logger.info("원시값 갱신 완료: %d건", len(notices))
        except Exception:
            logger.exception("원시값 갱신 중 오류 발생")

    def run_backfill(self) -> int:
        """초기 적재를 1회 수행한다 (스케줄러와 무관, FCM 발송 없음).

        비어 있는 Firestore 를 처음 채울 때 사용한다.
        이 경로를 거치지 않고 곧바로 상주 실행하면, 모집중 공고 전량이
        신규로 판정되어 전부 푸시가 나간다.

        수집 범위는 다른 잡과 동일하게 현재 연도 + status='RS02' 이다.

        Returns:
            저장된 공고 수.

        Raises:
            Exception: 크롤링·저장 중 발생한 예외를 그대로 전파한다.
                주기 잡과 달리 예외를 삼키지 않는다. 초기 적재는 1회성 수동
                작업이므로, 실패를 조용히 넘기면 부분 적재 상태로 상주 실행에
                들어가 남은 공고가 전량 푸시된다.
        """
        logger.info("초기 적재 시작: %s", datetime.now().isoformat())
        self._ensure_login()
        year = datetime.now().year
        notices = self._crawler.get_all_notices(year=year, status="RS02")
        count = self._notifier.process_new_notices(notices, backfill=True)
        logger.info("초기 적재 완료: %d건 저장, FCM 발송 0건", count)
        return count

    def setup(self, scheduler: Any) -> None:
        """apscheduler 인스턴스에 두 개의 잡을 등록한다.

        run_backfill() 은 주기 잡이 아니므로 등록하지 않는다.

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
            self.update_notices,
            trigger="interval",
            minutes=UPDATE_INTERVAL_MINUTES,
            max_instances=1,
            id="update_notices",
            name="원시값 갱신 (신청자·대기자·정원·마감)",
        )
