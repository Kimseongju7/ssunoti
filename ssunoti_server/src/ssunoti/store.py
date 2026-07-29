"""Firestore 저장 계층.

크롤러(SsupathCrawler)가 반환한 공고 dict 를 notices 컬렉션에
docId=notice_id 로 upsert 한다.

저장 규칙:
- 저장 필드: notice_id, title, url, content, deadline,
             applicant_count, waitlist_count, capacity, created_at (9개)
- 파생 플래그(is_closing_soon, notified_deadline 등)는 저장하지 않는다.
- set(merge=True) upsert. created_at 은 문서 최초 생성 시에만 기록한다.
- 비숫자 applicant_count/waitlist_count → 0, capacity → None (무제한·미정)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ssunoti.utils import build_url

logger = logging.getLogger(__name__)

_DETAIL_BASE_URL = (
    "https://path.ssu.ac.kr"
    "/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmInfo.do"
)
_COLLECTION = "notices"


def _to_int_or_zero(value: Any) -> int:
    """숫자 변환에 실패하면 0 을 반환한다.

    applicant_count, waitlist_count 에 사용한다.
    '-', None, 빈 문자열 등은 모두 0 으로 정규화한다.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def _to_int_or_none(value: Any) -> int | None:
    """숫자 변환에 실패하면 None 을 반환한다.

    capacity 에 사용한다.
    None 은 무제한 또는 미정을 뜻하며 0명 정원(int 0)과 구별된다.
    """
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _parse_deadline(application_period: dict | None) -> datetime | None:
    """application_period["end"] 문자열을 datetime 으로 변환한다.

    지원 형식:
        '2026.03.27 00:00'   — %Y.%m.%d %H:%M
        '2026.03.27'         — %Y.%m.%d

    변환에 실패하거나 값이 없으면 None 을 반환한다.
    """
    if not application_period:
        return None
    end_str = (application_period.get("end") or "").strip()
    if not end_str:
        return None
    for fmt in ("%Y.%m.%d %H:%M", "%Y.%m.%d"):
        try:
            return datetime.strptime(end_str, fmt)
        except ValueError:
            continue
    return None


def _build_doc_data(notice: dict, url: str) -> dict:
    """크롤러 공고 dict 를 Firestore 문서 데이터로 변환한다.

    created_at 은 포함하지 않는다.
    호출자(NoticeStore.upsert)가 문서 존재 여부를 확인한 뒤 추가한다.
    """
    return {
        "notice_id": notice.get("notice_id", ""),
        "title": notice.get("title", ""),
        "url": url,
        "content": notice.get("summary", ""),
        "deadline": _parse_deadline(notice.get("application_period")),
        "applicant_count": _to_int_or_zero(notice.get("applicant_count", 0)),
        "waitlist_count": _to_int_or_zero(notice.get("waitlist_count", 0)),
        "capacity": _to_int_or_none(notice.get("capacity")),
    }


class NoticeStore:
    """notices 컬렉션 Firestore 저장 계층."""

    def __init__(self, db: Any) -> None:
        """
        Args:
            db: Firestore 클라이언트.
                실환경: firebase_admin.firestore.client()
                테스트:  FakeFirestoreClient 등 호환 가능한 fake
        """
        self._db = db

    def exists(self, notice_id: str) -> bool:
        """notice_id 문서가 notices 컬렉션에 존재하는지 반환한다.

        문서의 존재 자체가 "이미 관측·알림 처리된 공고"를 뜻하므로,
        이 메서드가 신규 판별의 유일한 근거다.

        Args:
            notice_id: docId (encSddpbSeq 32자 hex)

        Returns:
            문서가 있으면 True. notice_id 가 비었으면 False.
        """
        if not notice_id:
            return False
        snapshot = self._db.collection(_COLLECTION).document(notice_id).get()
        return bool(snapshot.exists)

    def upsert(self, notice: dict) -> None:
        """공고 dict 를 notices 컬렉션에 upsert 한다.

        - docId = notice_id (encSddpbSeq 32자 hex)
        - set(merge=True) 기반 upsert
        - created_at 은 문서 최초 생성 시에만 기록하고 이후 보존한다.
        - 비숫자 applicant_count/waitlist_count → 0, capacity → None
        - 파생 플래그는 저장하지 않는다.

        Args:
            notice: SsupathCrawler.get_current_page_notices() 또는
                    get_all_notices() 가 반환한 공고 dict
        """
        notice_id: str = notice.get("notice_id", "")
        if not notice_id:
            logger.warning("notice_id 가 비어 있어 저장을 건너뜁니다.")
            return

        url = build_url(_DETAIL_BASE_URL, {"encSddpbSeq": notice_id})
        doc_ref = self._db.collection(_COLLECTION).document(notice_id)
        snapshot = doc_ref.get()

        data = _build_doc_data(notice, url)

        # created_at: 문서가 없을 때만 현재 시각을 기록한다.
        if not snapshot.exists:
            data["created_at"] = datetime.now(timezone.utc)

        doc_ref.set(data, merge=True)
        logger.debug(
            "upsert: notice_id=%s new=%s",
            notice_id,
            not snapshot.exists,
        )

    def upsert_many(self, notices: list[dict]) -> None:
        """복수 공고를 순서대로 upsert 한다.

        Args:
            notices: 공고 dict 목록
        """
        for notice in notices:
            self.upsert(notice)
