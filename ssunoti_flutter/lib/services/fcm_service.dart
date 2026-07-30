import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';

/// 서버가 신규 공고를 브로드캐스트하는 FCM topic.
///
/// 서버의 `ssunoti_server/src/ssunoti/notifier.py` 의 `_TOPIC` 과 반드시 같아야 한다.
/// 이 값이 어긋나면 알림이 조용히 사라진다 — 발송도 성공하고 구독도 성공하지만
/// 서로 다른 topic 이라 만나지 않는다.
const newNoticesTopic = 'new_notices';

/// FCM 구독을 관리한다.
///
/// 기기 토큰을 수집하지도 서버로 보내지도 않는다. 서버는 topic 브로드캐스트만
/// 사용하므로 사용자를 식별할 필요가 없다.
/// 근거: 단일 수집 계정 구조 — 사용자 자격증명·식별자를 다루지 않는다.
class FcmService {
  FcmService(this._messaging);

  final FirebaseMessaging _messaging;

  /// 알림 권한을 요청하고 topic 을 구독한다.
  ///
  /// 권한이 거부되어도 예외를 던지지 않는다. 알림은 부가 기능이고
  /// 공고 목록은 Firestore 에서 그대로 보이기 때문이다.
  Future<void> initialize() async {
    final settings = await _messaging.requestPermission();
    final granted =
        settings.authorizationStatus == AuthorizationStatus.authorized ||
            settings.authorizationStatus == AuthorizationStatus.provisional;

    if (!granted) {
      debugPrint('[FCM] 알림 권한 거부됨. topic 구독을 건너뛴다.');
      return;
    }

    // 웹은 topic 구독을 지원하지 않는다. Admin SDK 로만 가능하므로
    // 웹에서는 알림 없이 목록만 동작한다.
    if (kIsWeb) {
      debugPrint('[FCM] 웹은 topic 구독 미지원. 알림 없이 목록만 동작한다.');
      return;
    }

    await _messaging.subscribeToTopic(newNoticesTopic);
    debugPrint('[FCM] topic 구독 완료: $newNoticesTopic');
  }

  Future<void> unsubscribe() async {
    if (kIsWeb) return;
    await _messaging.unsubscribeFromTopic(newNoticesTopic);
  }

  /// 앱이 포그라운드일 때 도착한 메시지 스트림.
  ///
  /// 서버는 at-least-once 로 발송하므로 같은 공고가 두 번 올 수 있다.
  /// 표시하는 쪽에서 중복을 걸러야 한다.
  /// 근거: docs/adr/0002-send-before-persist-at-least-once.md
  Stream<RemoteMessage> get onForegroundMessage => FirebaseMessaging.onMessage;
}
