"""SSUNoti 서버 진입점.

APScheduler 를 구성하고 기동한다.
Firebase Admin SDK 는 GOOGLE_APPLICATION_CREDENTIALS 환경변수가 가리키는
서비스 계정 키 파일로 초기화한다. 키 파일은 저장소에 커밋하지 않는다.
"""
from __future__ import annotations

import logging
import os
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def _init_firebase() -> None:
    """Firebase Admin SDK 를 초기화한다.

    Raises:
        EnvironmentError: GOOGLE_APPLICATION_CREDENTIALS 환경변수가 없을 때.
    """
    import firebase_admin
    from firebase_admin import credentials

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise EnvironmentError(
            "GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다. "
            "Firebase 서비스 계정 키 파일 경로를 지정하세요."
        )
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK 초기화 완료")


def _build_scheduler():
    """스케줄러를 구성하고 반환한다 (start() 는 호출하지 않는다)."""
    from apscheduler.schedulers.background import BackgroundScheduler
    from firebase_admin import firestore, messaging

    from ssunoti.crawler import SsupathCrawler
    from ssunoti.notifier import NoticeNotifier
    from ssunoti.scheduler import NoticeScheduler
    from ssunoti.store import NoticeStore

    db = firestore.client()
    store = NoticeStore(db)

    crawler = SsupathCrawler()
    logger.info("SSUPath 로그인 시도")
    crawler.login()
    logger.info("SSUPath 로그인 완료")

    notifier = NoticeNotifier(store, messaging)

    notice_scheduler = NoticeScheduler(crawler, notifier, store)
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    notice_scheduler.setup(scheduler)
    return scheduler


def main() -> None:
    """스케줄러를 구성하고 기동한다."""
    logger.info("SSUNoti 서버 시작")
    try:
        _init_firebase()
        scheduler = _build_scheduler()
        scheduler.start()
        logger.info("스케줄러 기동 완료 — 상주 실행 중")
        try:
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            logger.info("종료 신호 수신")
    except Exception:
        logger.exception("서버 기동 중 치명 오류 발생")
        sys.exit(1)
    finally:
        logger.info("SSUNoti 서버 종료")


if __name__ == "__main__":
    main()
