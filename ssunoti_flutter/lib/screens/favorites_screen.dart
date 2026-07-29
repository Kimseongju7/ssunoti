import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/favorites_provider.dart';
import 'notice_list_screen.dart';

/// 찜한 공고 목록.
///
/// 별도로 저장된 목록이 아니라 찜 ID 집합과 Firestore 스트림의 교집합이다.
/// 그래서 서버가 제목·정원을 갱신하면 이 화면도 함께 갱신된다.
class FavoritesScreen extends ConsumerWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favorites = ref.watch(favoriteNoticesProvider);
    final favoriteIds = ref.watch(favoriteIdsProvider);
    final closingSoon = ref.watch(closingSoonFavoritesProvider);

    if (favoriteIds.isEmpty) {
      return const _FavoritesEmpty(
        message: '찜한 공고가 없습니다',
        hint: '공고 목록에서 하트를 눌러 찜해두면 여기에 모입니다',
      );
    }

    // 찜은 했지만 서버 목록에 없는 경우. 모집이 끝나 서버가 더 이상 수집하지
    // 않는 공고다. ID 는 남아 있지만 보여줄 내용이 없다.
    if (favorites.isEmpty) {
      return const _FavoritesEmpty(
        message: '찜한 공고가 모두 모집 마감되었습니다',
        hint: '새 공고를 찜해보세요',
      );
    }

    return Column(
      children: [
        if (closingSoon.isNotEmpty)
          _ClosingSoonBanner(count: closingSoon.length),
        Expanded(child: NoticeListView(notices: favorites)),
      ],
    );
  }
}

/// 찜한 공고 중 마감 임박 건이 있을 때 띄우는 배너.
///
/// 마감 임박 판단을 서버가 못 하는 이유는 서버가 찜을 모르기 때문이다.
/// 그래서 이 알림은 푸시가 아니라 앱 내 배너다.
class _ClosingSoonBanner extends StatelessWidget {
  const _ClosingSoonBanner({required this.count});

  final int count;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: Colors.deepOrange.withValues(alpha: 0.10),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Row(
        children: [
          const Icon(Icons.alarm, size: 18, color: Colors.deepOrange),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '찜한 공고 $count건이 곧 마감됩니다',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.deepOrange,
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FavoritesEmpty extends StatelessWidget {
  const _FavoritesEmpty({required this.message, required this.hint});

  final String message;
  final String hint;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.favorite_border,
              size: 48,
              color: Theme.of(context).disabledColor,
            ),
            const SizedBox(height: 12),
            Text(message, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 6),
            Text(
              hint,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
