import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/notice.dart';
import 'notices_provider.dart';

/// 찜 목록을 담는 SharedPreferences 키.
const favoritesStorageKey = 'favorite_notice_ids';

/// SharedPreferences 인스턴스.
///
/// main() 에서 override 로 실제 인스턴스를 주입한다. 테스트에서는
/// SharedPreferences.setMockInitialValues() 로 대체한다.
final sharedPreferencesProvider = Provider<SharedPreferences>(
  (ref) => throw UnimplementedError('main() 에서 override 해야 한다'),
);

/// 찜한 공고의 notice_id 집합.
///
/// 찜은 기기 로컬에만 저장한다. 서버로 나가지 않으므로 로그인이 필요 없다.
/// 저장하는 것은 ID 뿐이고, 공고 내용은 Firestore 스트림에서 온다.
class FavoriteIdsNotifier extends Notifier<Set<String>> {
  @override
  Set<String> build() {
    final prefs = ref.watch(sharedPreferencesProvider);
    return prefs.getStringList(favoritesStorageKey)?.toSet() ?? <String>{};
  }

  bool contains(String noticeId) => state.contains(noticeId);

  /// 찜 상태를 뒤집고 저장한다.
  Future<void> toggle(String noticeId) async {
    final next = {...state};
    if (!next.remove(noticeId)) {
      next.add(noticeId);
    }
    state = next;
    await _persist(next);
  }

  Future<void> clear() async {
    state = <String>{};
    await _persist(const <String>{});
  }

  Future<void> _persist(Set<String> ids) async {
    final prefs = ref.read(sharedPreferencesProvider);
    await prefs.setStringList(favoritesStorageKey, ids.toList(growable: false));
  }
}

final favoriteIdsProvider =
    NotifierProvider<FavoriteIdsNotifier, Set<String>>(FavoriteIdsNotifier.new);

/// 특정 공고의 찜 여부. 하트 아이콘이 이것만 구독하면 목록 전체가 다시 그려지지 않는다.
final isFavoriteProvider = Provider.family<bool, String>(
  (ref, noticeId) => ref.watch(favoriteIdsProvider).contains(noticeId),
);

/// 찜한 공고 목록.
///
/// 찜 ID 집합과 Firestore 스트림의 교집합이다. 둘 중 하나만 바뀌어도
/// 자동으로 다시 계산된다 — 화면 간 배선이 필요 없는 이유.
final favoriteNoticesProvider = Provider<List<Notice>>((ref) {
  final ids = ref.watch(favoriteIdsProvider);
  final notices = ref.watch(noticesProvider).value ?? const <Notice>[];
  return notices
      .where((notice) => ids.contains(notice.noticeId))
      .toList(growable: false);
});

/// 찜한 공고 중 마감이 임박한 것.
///
/// 마감 임박 알림은 서버가 아니라 앱이 판단한다. 찜은 서버가 모르기 때문이다.
final closingSoonFavoritesProvider = Provider<List<Notice>>((ref) {
  final favorites = ref.watch(favoriteNoticesProvider);
  return favorites
      .where((notice) => notice.isDeadlineNear() ?? false)
      .toList(growable: false);
});
