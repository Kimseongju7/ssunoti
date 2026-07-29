import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/notice.dart';

/// Firestore 인스턴스. 테스트에서 override 해 fake 를 주입한다.
final firestoreProvider = Provider<FirebaseFirestore>(
  (ref) => FirebaseFirestore.instance,
);

/// `notices` 컬렉션 실시간 스트림.
///
/// 서버가 15분마다 원시값을 갱신하므로 앱은 별도 새로고침 없이 최신값을 받는다.
/// 최근 등록순 정렬.
final noticesProvider = StreamProvider<List<Notice>>((ref) {
  final db = ref.watch(firestoreProvider);
  return db
      .collection('notices')
      .orderBy('created_at', descending: true)
      .snapshots()
      .map(
        (snapshot) =>
            snapshot.docs.map(Notice.fromFirestore).toList(growable: false),
      );
});

/// 마감이 지나지 않은 공고만.
///
/// 서버는 모집중(RS02)만 수집하지만 마감 시각이 지난 뒤에도 다음 수집까지는
/// 문서가 남아 있다. 그래서 표시 시점에 한 번 더 거른다.
final openNoticesProvider = Provider<List<Notice>>((ref) {
  final notices = ref.watch(noticesProvider).value ?? const <Notice>[];
  return notices.where((n) => !n.isClosed()).toList(growable: false);
});

/// notice_id 로 단건 조회. 목록 스트림에서 찾으므로 추가 읽기가 없다.
final noticeByIdProvider = Provider.family<Notice?, String>((ref, noticeId) {
  final notices = ref.watch(noticesProvider).value ?? const <Notice>[];
  for (final notice in notices) {
    if (notice.noticeId == noticeId) return notice;
  }
  return null;
});
