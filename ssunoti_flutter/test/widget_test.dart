import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ssunoti_flutter/providers/favorites_provider.dart';

/// 찜 상태 검증.
///
/// 이 앱에서 상태관리를 도입한 이유가 "찜 상태를 세 화면이 공유한다" 였다.
/// 그 공유가 실제로 성립하는지, 그리고 기기 재시작 후에도 남는지 확인한다.
void main() {
  ProviderContainer makeContainer(SharedPreferences prefs) {
    final container = ProviderContainer(
      overrides: [sharedPreferencesProvider.overrideWithValue(prefs)],
    );
    addTearDown(container.dispose);
    return container;
  }

  const noticeA = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
  const noticeB = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';

  group('FavoriteIdsNotifier', () {
    test('초기 상태는 비어 있다', () async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final container = makeContainer(prefs);

      expect(container.read(favoriteIdsProvider), isEmpty);
    });

    test('toggle 하면 추가되고 다시 toggle 하면 빠진다', () async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final container = makeContainer(prefs);
      final notifier = container.read(favoriteIdsProvider.notifier);

      await notifier.toggle(noticeA);
      expect(container.read(favoriteIdsProvider), {noticeA});

      await notifier.toggle(noticeA);
      expect(container.read(favoriteIdsProvider), isEmpty);
    });

    test('toggle 결과가 SharedPreferences 에 저장된다', () async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final container = makeContainer(prefs);

      await container.read(favoriteIdsProvider.notifier).toggle(noticeA);

      expect(prefs.getStringList(favoritesStorageKey), [noticeA]);
    });

    test('저장된 찜 목록을 기동 시 복원한다', () async {
      SharedPreferences.setMockInitialValues({
        favoritesStorageKey: [noticeA, noticeB],
      });
      final prefs = await SharedPreferences.getInstance();
      final container = makeContainer(prefs);

      expect(container.read(favoriteIdsProvider), {noticeA, noticeB});
    });

    test('clear 하면 전부 지워진다', () async {
      SharedPreferences.setMockInitialValues({
        favoritesStorageKey: [noticeA, noticeB],
      });
      final prefs = await SharedPreferences.getInstance();
      final container = makeContainer(prefs);

      await container.read(favoriteIdsProvider.notifier).clear();

      expect(container.read(favoriteIdsProvider), isEmpty);
      expect(prefs.getStringList(favoritesStorageKey), isEmpty);
    });
  });

  group('isFavoriteProvider', () {
    test('찜 여부를 공고별로 알려준다', () async {
      SharedPreferences.setMockInitialValues({
        favoritesStorageKey: [noticeA],
      });
      final prefs = await SharedPreferences.getInstance();
      final container = makeContainer(prefs);

      expect(container.read(isFavoriteProvider(noticeA)), isTrue);
      expect(container.read(isFavoriteProvider(noticeB)), isFalse);
    });

    test('한 곳에서 toggle 하면 다른 구독자도 값이 바뀐다', () async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final container = makeContainer(prefs);

      // 목록 화면의 하트가 구독한다고 가정
      final subscription = container.listen(
        isFavoriteProvider(noticeA),
        (_, _) {},
        fireImmediately: true,
      );
      expect(subscription.read(), isFalse);

      // 상세 화면에서 눌렀다고 가정
      await container.read(favoriteIdsProvider.notifier).toggle(noticeA);

      expect(subscription.read(), isTrue);
    });
  });
}
