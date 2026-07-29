import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/notice.dart';
import '../providers/notices_provider.dart';
import '../widgets/notice_card.dart';
import 'notice_detail_screen.dart';

/// 전체 공고 목록. Firestore 스트림을 그대로 그린다.
class NoticeListScreen extends ConsumerWidget {
  const NoticeListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final noticesAsync = ref.watch(noticesProvider);

    return noticesAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => _ErrorView(message: '$error'),
      data: (_) {
        final notices = ref.watch(openNoticesProvider);
        if (notices.isEmpty) {
          return const _EmptyView(
            icon: Icons.inbox_outlined,
            message: '모집 중인 공고가 없습니다',
          );
        }
        return NoticeListView(notices: notices);
      },
    );
  }
}

/// 공고 목록 뷰. 목록 화면과 찜 화면이 함께 쓴다.
class NoticeListView extends StatelessWidget {
  const NoticeListView({super.key, required this.notices});

  final List<Notice> notices;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: notices.length,
      itemBuilder: (context, index) {
        final notice = notices[index];
        return NoticeCard(
          notice: notice,
          onTap: () => Navigator.of(context).push(
            MaterialPageRoute<void>(
              builder: (_) => NoticeDetailScreen(noticeId: notice.noticeId),
            ),
          ),
        );
      },
    );
  }
}

class _EmptyView extends StatelessWidget {
  const _EmptyView({required this.icon, required this.message});

  final IconData icon;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 48, color: Theme.of(context).disabledColor),
          const SizedBox(height: 12),
          Text(message, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, size: 48),
            const SizedBox(height: 12),
            Text(
              '공고를 불러오지 못했습니다',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 6),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
