"""FCM 알림 계층 (notifier.py) 단위 테스트.

Firestore 와 FCM Admin SDK 는 모두 fake 로 대체한다.
실제 Firebase 프로젝트에 쓰기를 하지 않는다.

검증 항목:
(a) 문서가 없는 notice_id 1건당 send 호출이 정확히 1회이고,
    topic 대상이며, payload 에 기기 토큰이 포함되지 않는다.
(b) 정상 완주한 사이클을 재실행하면 send 호출이 0회다.
(c) send 성공 직후 Firestore 쓰기 전에 예외로 중단시킨 뒤
    사이클을 재실행하면 해당 공고에 대해 send 가 다시 호출된다
    (중복 허용, 유실 없음).
(d) send 가 실패한 공고는 Firestore 에 문서가 기록되지 않는다.
"""
from __future__ import annotations

from typing import Any

import pytest

from ssunoti.notifier import NoticeNotifier
from ssunoti.store import NoticeStore


# ── Fake Firestore ────────────────────────────────────────────────────────────


class _FakeSnapshot:
    def __init__(self, data: dict | None) -> None:
        self._data = data
        self.exists = data is not None

    def to_dict(self) -> dict:
        return self._data.copy() if self._data else {}


class _FakeDocRef:
    def __init__(self, collection_store: dict, doc_id: str) -> None:
        self._store = collection_store
        self._doc_id = doc_id
        self.raise_on_set: Exception | None = None

    def get(self) -> _FakeSnapshot:
        return _FakeSnapshot(self._store.get(self._doc_id))

    def set(self, data: dict, merge: bool = False) -> None:
        if self.raise_on_set is not None:
            raise self.raise_on_set
        existing = self._store.get(self._doc_id)
        if merge and existing is not None:
            self._store[self._doc_id] = {**existing, **data}
        else:
            self._store[self._doc_id] = data.copy()


class _FakeCollection:
    def __init__(self) -> None:
        self._docs: dict[str, dict] = {}
        self._refs: dict[str, _FakeDocRef] = {}

    def document(self, doc_id: str) -> _FakeDocRef:
        if doc_id not in self._refs:
            self._refs[doc_id] = _FakeDocRef(self._docs, doc_id)
        return self._refs[doc_id]

    def all_docs(self) -> dict[str, dict]:
        return dict(self._docs)


class FakeFirestoreClient:
    def __init__(self) -> None:
        self._collections: dict[str, _FakeCollection] = {}

    def collection(self, name: str) -> _FakeCollection:
        if name not in self._collections:
            self._collections[name] = _FakeCollection()
        return self._collections[name]

    def get_docs(self, collection_name: str) -> dict[str, dict]:
        col = self._collections.get(collection_name)
        return col.all_docs() if col else {}


# ── Fake FCM messaging ────────────────────────────────────────────────────────


class FakeMessaging:
    """firebase_admin.messaging 모듈 호환 fake.

    send_calls 에 전송된 Message 객체를 누적한다.
    raise_on_send 를 설정하면 send() 에서 예외를 발생시킨다.
    """

    class Message:
        """FCM 메시지."""

        def __init__(
            self,
            notification: Any = None,
            topic: str | None = None,
            token: str | None = None,
            **kwargs: Any,
        ) -> None:
            self.notification = notification
            self.topic = topic
            self.token = token

    class Notification:
        """FCM 알림 페이로드."""

        def __init__(self, title: str = "", body: str = "") -> None:
            self.title = title
            self.body = body

    def __init__(self) -> None:
        self.send_calls: list[Any] = []
        self.raise_on_send: Exception | None = None

    def send(self, message: Any) -> str:
        if self.raise_on_send is not None:
            raise self.raise_on_send
        self.send_calls.append(message)
        return f"projects/test/messages/{len(self.send_calls)}"


# ── 테스트용 공고 팩토리 ───────────────────────────────────────────────────────


def _make_notice(
    notice_id: str = "aaaa0000aaaa0000aaaa0000aaaa0000",
    title: str = "테스트 공고",
) -> dict:
    """테스트용 공고 dict (합성 notice_id 32자, 실계정 정보 미포함)."""
    return {
        "notice_id": notice_id,
        "title": title,
        "summary": "테스트 공고 요약",
        "application_period": {"start": "2026.04.01 00:00", "end": "2026.04.30 23:59"},
        "applicant_count": 5,
        "waitlist_count": 0,
        "capacity": 30,
        "status": "모집중",
    }


# ── pytest fixtures ───────────────────────────────────────────────────────────


@pytest.fixture()
def db() -> FakeFirestoreClient:
    return FakeFirestoreClient()


@pytest.fixture()
def store(db: FakeFirestoreClient) -> NoticeStore:
    return NoticeStore(db)


@pytest.fixture()
def messaging() -> FakeMessaging:
    return FakeMessaging()


@pytest.fixture()
def notifier(store: NoticeStore, messaging: FakeMessaging) -> NoticeNotifier:
    return NoticeNotifier(store, messaging)


# ── (a) 신규 공고 1건당 send 1회, topic 대상, 기기 토큰 없음 ────────────────────


class TestSendOnce:
    """(a) 문서가 없는 notice_id 1건당 send 가 정확히 1회, topic 대상, 기기 토큰 없음."""

    def test_single_new_notice_sends_exactly_once(
        self, notifier: NoticeNotifier, messaging: FakeMessaging
    ) -> None:
        """새 공고 1건에 대해 send 가 정확히 1회 호출된다."""
        notifier.process_new_notices([_make_notice()])
        assert len(messaging.send_calls) == 1

    def test_multiple_new_notices_send_per_notice(
        self, notifier: NoticeNotifier, messaging: FakeMessaging
    ) -> None:
        """새 공고 N건에 대해 send 가 정확히 N회 호출된다."""
        notices = [
            _make_notice("id10000000000000000000000000000a"),
            _make_notice("id20000000000000000000000000000b"),
            _make_notice("id30000000000000000000000000000c"),
        ]
        notifier.process_new_notices(notices)
        assert len(messaging.send_calls) == 3

    def test_message_targets_topic_not_token(
        self, notifier: NoticeNotifier, messaging: FakeMessaging
    ) -> None:
        """메시지가 topic 대상이며 기기 토큰을 포함하지 않는다."""
        notifier.process_new_notices([_make_notice()])

        assert len(messaging.send_calls) == 1
        message = messaging.send_calls[0]
        assert message.topic is not None, "topic 이 설정되어 있어야 한다"
        assert message.token is None, "기기 토큰이 payload 에 포함되면 안 된다"

    def test_message_has_notification_payload(
        self, notifier: NoticeNotifier, messaging: FakeMessaging
    ) -> None:
        """메시지에 공고 제목이 담긴 notification 페이로드가 포함된다."""
        notifier.process_new_notices([_make_notice(title="특정 공고 제목")])

        message = messaging.send_calls[0]
        assert message.notification is not None
        assert "특정 공고 제목" in message.notification.body


# ── (b) 정상 완주 후 재실행 시 send 0회 ─────────────────────────────────────────


class TestNoResend:
    """(b) 정상 완주한 사이클을 재실행하면 send 호출이 0회다."""

    def test_completed_cycle_does_not_resend(
        self, notifier: NoticeNotifier, messaging: FakeMessaging
    ) -> None:
        """1회 성공 후 동일 공고 집합으로 재실행하면 send 가 호출되지 않는다."""
        notices = [
            _make_notice("resend0010000000000000000000000a"),
            _make_notice("resend0020000000000000000000000b"),
        ]

        notifier.process_new_notices(notices)
        assert len(messaging.send_calls) == 2

        # 사이클 재실행: 모든 문서가 이미 Firestore 에 존재
        send_count_before = len(messaging.send_calls)
        notifier.process_new_notices(notices)
        send_count_after = len(messaging.send_calls)

        assert send_count_after == send_count_before, (
            f"재실행 시 send 가 호출되면 안 됩니다. "
            f"이전: {send_count_before}, 이후: {send_count_after}"
        )


# ── (c) FCM 성공 → Firestore 실패 → 재실행 시 재발송 ──────────────────────────


class TestAtLeastOnce:
    """(c) send 성공 직후 Firestore 쓰기 실패 → 다음 사이클에서 재발송."""

    def test_write_failure_after_send_causes_resend(
        self,
        notifier: NoticeNotifier,
        messaging: FakeMessaging,
        db: FakeFirestoreClient,
    ) -> None:
        """FCM 발송 성공 → Firestore 쓰기 예외 → 재실행 시 send 다시 호출."""
        notice = _make_notice("atleast001000000000000000000000a")
        notice_id = notice["notice_id"]

        # Firestore 쓰기가 예외를 발생시키도록 설정
        doc_ref = db.collection("notices").document(notice_id)
        doc_ref.raise_on_set = RuntimeError("Firestore 쓰기 실패 시뮬레이션")

        # 사이클 1: FCM 발송 성공, Firestore 쓰기 실패
        with pytest.raises(RuntimeError):
            notifier.process_new_notices([notice])

        # FCM 은 1회 발송되었다
        assert len(messaging.send_calls) == 1
        # 문서는 저장되지 않았다 (유실 없음 조건 확인)
        assert notice_id not in db.get_docs("notices")

        # Firestore 쓰기 복구
        doc_ref.raise_on_set = None

        # 사이클 2: 문서가 여전히 없으므로 send 재호출 (중복 허용)
        notifier.process_new_notices([notice])

        assert len(messaging.send_calls) == 2, (
            "Firestore 쓰기 실패 후 재실행 시 send 가 다시 호출되어야 합니다"
        )
        # 이제 문서가 저장되었다
        assert notice_id in db.get_docs("notices")


# ── (d) FCM 실패 시 Firestore 에 문서 기록 안 함 ───────────────────────────────


class TestNoWriteOnSendFailure:
    """(d) send 가 실패한 공고는 Firestore 에 문서가 기록되지 않는다."""

    def test_send_failure_does_not_write_firestore(
        self,
        notifier: NoticeNotifier,
        messaging: FakeMessaging,
        db: FakeFirestoreClient,
    ) -> None:
        """FCM 발송 실패 시 Firestore 에 문서를 기록하지 않는다."""
        notice = _make_notice("failsend001000000000000000000001")
        notice_id = notice["notice_id"]

        messaging.raise_on_send = Exception("FCM 발송 실패 시뮬레이션")
        notifier.process_new_notices([notice])

        assert notice_id not in db.get_docs("notices"), (
            "FCM 발송 실패 시 Firestore 에 문서를 기록하면 안 됩니다"
        )

    def test_send_failure_does_not_raise_out(
        self, notifier: NoticeNotifier, messaging: FakeMessaging
    ) -> None:
        """FCM 발송 실패가 process_new_notices 밖으로 전파되지 않는다."""
        notice = _make_notice("failsend002000000000000000000002")
        messaging.raise_on_send = Exception("FCM 발송 실패 시뮬레이션")

        # 예외가 전파되지 않아야 한다 (건너뜀 처리)
        notifier.process_new_notices([notice])

    def test_partial_send_failure_does_not_block_others(
        self,
        notifier: NoticeNotifier,
        messaging: FakeMessaging,
        db: FakeFirestoreClient,
    ) -> None:
        """일부 공고 FCM 발송 실패가 다른 공고 처리를 막지 않는다."""
        notice_fail = _make_notice("failsend003000000000000000000003")
        notice_ok = _make_notice("failsend004000000000000000000004")

        # 첫 번째 send 만 실패, 이후 send 는 정상 동작
        call_count = [0]

        def side_effect(message: Any) -> str:
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("첫 번째 발송 실패")
            messaging.send_calls.append(message)
            return f"projects/test/messages/{len(messaging.send_calls)}"

        messaging.send = side_effect  # type: ignore[method-assign]

        notifier.process_new_notices([notice_fail, notice_ok])

        docs = db.get_docs("notices")
        assert notice_fail["notice_id"] not in docs, "발송 실패 공고는 저장되면 안 됩니다"
        assert notice_ok["notice_id"] in docs, "발송 성공 공고는 저장되어야 합니다"
