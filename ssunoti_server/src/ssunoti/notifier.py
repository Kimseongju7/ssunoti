"""FCM 알림 계층 및 신규 공고 처리 사이클.

신규 판정 기준: notices 컬렉션에 notice_id 문서가 없음.
처리 순서: FCM topic 브로드캐스트 발송 → Firestore 쓰기.
발송 성공 이후에만 문서를 기록하므로, 중간 실패 시 다음 사이클에서 재발송된다(at-least-once).

기기 토큰을 수집하거나 payload 에 포함하지 않는다.
정원 임박·마감 임박 알림은 이 모듈의 범위 밖이다.
"""
from __future__ import annotations

import logging
from typing import Any

from ssunoti.store import NoticeStore

logger = logging.getLogger(__name__)

_TOPIC = "new_notices"
_COLLECTION = "notices"
_NOTIFICATION_TITLE = "새 비교과 공고"


class NoticeNotifier:
    """신규 공고 FCM 알림 계층.

    notices 컬렉션에 문서가 없는 공고를 신규로 판단하고:
    1. FCM topic 브로드캐스트를 발송한다.
    2. 발송이 성공한 뒤에만 Firestore 에 문서를 기록한다.

    이 순서가 at-least-once 보장의 근거이다.
    - FCM 실패 → 건너뜀, Firestore 기록 안 함, 다음 사이클에서 재시도.
    - FCM 성공 후 Firestore 실패 → 예외 전파, 다음 사이클에서 FCM 재발송(중복 허용).
    """

    def __init__(self, store: NoticeStore, messaging: Any) -> None:
        """
        Args:
            store: NoticeStore 인스턴스 (Firestore 저장 계층)
            messaging: firebase_admin.messaging 모듈 또는 호환 fake.
                       Message, Notification 클래스와 send() 함수를 제공해야 한다.
        """
        self._store = store
        self._messaging = messaging

    def _is_new_notice(self, notice_id: str) -> bool:
        """notice_id 에 해당하는 Firestore 문서가 없으면 True (신규 공고)."""
        doc_ref = self._store._db.collection(_COLLECTION).document(notice_id)
        snapshot = doc_ref.get()
        return not snapshot.exists

    def _send_topic_broadcast(self, notice: dict) -> None:
        """FCM topic 브로드캐스트를 발송한다.

        topic 발송만 사용한다. 기기 토큰을 포함하지 않는다.

        Args:
            notice: 공고 dict (title 필드 사용)
        Raises:
            Exception: FCM SDK 에서 발생한 예외를 그대로 전파한다.
        """
        message = self._messaging.Message(
            notification=self._messaging.Notification(
                title=_NOTIFICATION_TITLE,
                body=notice.get("title", ""),
            ),
            topic=_TOPIC,
        )
        self._messaging.send(message)
        logger.debug(
            "FCM 발송 완료: notice_id=%s topic=%s",
            notice.get("notice_id"),
            _TOPIC,
        )

    def process_new_notices(
        self, notices: list[dict], *, backfill: bool = False
    ) -> int:
        """공고 목록을 처리한다.

        backfill=False (기본, 일반 모드):
            1. notice_id 가 Firestore 에 없으면 신규 공고로 판단한다.
            2. FCM topic 브로드캐스트를 발송한다.
            3. 발송 성공 이후에만 Firestore 쓰기를 수행한다.

            FCM 발송 실패: 해당 공고를 건너뛴다. Firestore 에 기록하지 않는다.
            Firestore 쓰기 실패: 예외를 전파한다. 다음 사이클에서 재발송된다.

        backfill=True (초기 적재 모드):
            FCM 발송 없이 수집된 공고 전량을 Firestore 에 저장한다.
            빈 Firestore 를 최초로 채울 때 사용한다.
            신규 판정을 수행하지 않으며, FCM 은 한 건도 발송하지 않는다.

        Args:
            notices: 크롤러가 반환한 공고 dict 목록 (notice_id 필드 포함)
            backfill: True 이면 초기 적재 모드로 동작한다. (기본값: False)

        Returns:
            이번 사이클에서 Firestore 저장이 완료된 공고 수
        """
        if backfill:
            return self._process_backfill(notices)
        return self._process_normal(notices)

    def _process_backfill(self, notices: list[dict]) -> int:
        """초기 적재 모드: FCM 발송 없이 전체 공고를 Firestore 에 저장한다."""
        count = 0
        for notice in notices:
            notice_id = notice.get("notice_id", "")
            if not notice_id:
                continue
            self._store.upsert(notice)
            count += 1
            logger.debug("backfill upsert: notice_id=%s", notice_id)
        logger.info("backfill 완료: %d건 저장", count)
        return count

    def _process_normal(self, notices: list[dict]) -> int:
        """일반 모드: 신규 공고만 FCM 발송 후 Firestore 에 저장한다."""
        count = 0
        for notice in notices:
            notice_id = notice.get("notice_id", "")
            if not notice_id:
                continue

            if not self._is_new_notice(notice_id):
                continue

            try:
                self._send_topic_broadcast(notice)
            except Exception:
                logger.exception(
                    "FCM 발송 실패 — 이번 사이클에서 건너뜁니다: notice_id=%s",
                    notice_id,
                )
                continue  # 발송 실패 → Firestore 기록 안 함

            # FCM 발송 성공 이후에만 Firestore 쓰기 (예외 시 전파됨)
            self._store.upsert(notice)
            count += 1

        return count
