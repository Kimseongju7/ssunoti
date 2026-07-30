"""SSUNoti 서버 진입점.

두 가지 모드가 있다.

    uv run python main.py --backfill    # 초기 적재 1회 후 종료 (FCM 발송 0건)
    uv run python main.py               # 상주 실행 (스케줄러 기동)

빈 Firestore 에 처음 데이터를 채울 때는 반드시 --backfill 을 먼저 1회 실행한다.
신규 판정 기준이 "문서가 존재하지 않음" 이므로, 곧바로 상주 실행하면
모집중 공고 전량이 신규로 판정되어 전부 푸시가 나간다.

Firebase Admin SDK 는 GOOGLE_APPLICATION_CREDENTIALS 환경변수가 가리키는
서비스 계정 키 파일로 초기화한다. 키 파일은 저장소에 커밋하지 않는다.
"""
from __future__ import annotations

import argparse
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


def _build_notice_scheduler():
    """크롤러·저장소·알리미를 조립한 NoticeScheduler 를 반환한다.

    이 시점에 SSUPath 로그인을 1회 수행한다.
    backfill 모드와 상주 모드가 이 조립 과정을 공유한다.
    """
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
    return NoticeScheduler(crawler, notifier, store)


def _build_scheduler():
    """잡이 등록된 BackgroundScheduler 를 반환한다 (start() 는 호출하지 않는다)."""
    from apscheduler.schedulers.background import BackgroundScheduler

    notice_scheduler = _build_notice_scheduler()
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    notice_scheduler.setup(scheduler)
    return scheduler


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        prog="ssunoti-server",
        description="SSUPath 비교과 공고 수집·알림 서버",
    )
    parser.add_argument(
        "--backfill",
        action="store_true",
        help=(
            "초기 적재 모드. 수집한 공고를 저장만 하고 FCM 은 한 건도 발송하지 "
            "않은 뒤 종료한다. 빈 Firestore 를 처음 채울 때 1회 실행한다."
        ),
    )
    return parser.parse_args(argv)


def _run_backfill() -> None:
    """초기 적재를 1회 수행하고 종료한다 (스케줄러 기동 없음)."""
    logger.info("초기 적재 모드 — FCM 발송 없이 저장만 수행합니다")
    notice_scheduler = _build_notice_scheduler()
    count = notice_scheduler.run_backfill()
    logger.info("초기 적재 종료: %d건 저장", count)


def _run_forever() -> None:
    """스케줄러를 기동하고 상주 실행한다."""
    scheduler = _build_scheduler()
    scheduler.start()
    logger.info("스케줄러 기동 완료 — 상주 실행 중")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("종료 신호 수신")


def main(argv: list[str] | None = None) -> None:
    """진입점. --backfill 이면 1회 적재 후 종료, 아니면 상주 실행한다."""
    args = _parse_args(argv)
    logger.info("SSUNoti 서버 시작 (backfill=%s)", args.backfill)
    try:
        _init_firebase()
        if args.backfill:
            _run_backfill()
        else:
            _run_forever()
    except Exception:
        logger.exception("서버 기동 중 치명 오류 발생")
        sys.exit(1)
    finally:
        logger.info("SSUNoti 서버 종료")


if __name__ == "__main__":
    main()
