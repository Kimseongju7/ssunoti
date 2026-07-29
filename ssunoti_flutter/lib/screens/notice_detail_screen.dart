import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/notice.dart';
import '../providers/favorites_provider.dart';
import '../providers/notices_provider.dart';

final _dateTimeFormat = DateFormat('yyyy.MM.dd HH:mm');

/// 공고 상세.
///
/// notice_id 만 받아 목록 스트림에서 찾는다. 공고 객체를 통째로 넘기면
/// 서버가 값을 갱신해도 이 화면은 옛 값을 계속 보여준다.
class NoticeDetailScreen extends ConsumerWidget {
  const NoticeDetailScreen({super.key, required this.noticeId});

  final String noticeId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notice = ref.watch(noticeByIdProvider(noticeId));
    final isFavorite = ref.watch(isFavoriteProvider(noticeId));

    if (notice == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('공고')),
        body: const Center(child: Text('공고를 찾을 수 없습니다')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('공고 상세'),
        actions: [
          IconButton(
            icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border),
            color: isFavorite ? Colors.redAccent : null,
            tooltip: isFavorite ? '찜 해제' : '찜하기',
            onPressed: () =>
                ref.read(favoriteIdsProvider.notifier).toggle(noticeId),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(notice.title, style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 16),
          _InfoTable(notice: notice),
          const Divider(height: 32),
          if (notice.content.isNotEmpty)
            Text(notice.content, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
      bottomNavigationBar: _ApplyBar(url: notice.url),
    );
  }
}

class _InfoTable extends StatelessWidget {
  const _InfoTable({required this.notice});

  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final capacity = notice.capacity;
    final deadline = notice.deadline;

    return Column(
      children: [
        _InfoRow(
          label: '모집 정원',
          // 정원 미상을 0 으로 표시하지 않는다.
          value: capacity == null ? '미정 또는 무제한' : '$capacity명',
        ),
        _InfoRow(label: '신청자', value: '${notice.applicantCount}명'),
        _InfoRow(label: '대기자', value: '${notice.waitlistCount}명'),
        _InfoRow(
          label: '신청 마감',
          value: deadline == null
              ? '상시모집'
              : '${_dateTimeFormat.format(deadline)}'
                  '${_remainingSuffix(notice)}',
        ),
      ],
    );
  }

  String _remainingSuffix(Notice notice) {
    final remaining = notice.daysUntilDeadline();
    if (remaining == null) return '';
    if (remaining < 0) return ' (마감됨)';
    if (remaining == 0) return ' (오늘 마감)';
    return ' (D-$remaining)';
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 88,
            child: Text(
              label,
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.copyWith(color: Theme.of(context).hintColor),
            ),
          ),
          Expanded(
            child: Text(value, style: Theme.of(context).textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }
}

/// 신청 버튼.
///
/// 앱이 신청을 대행하지 않는다. SSUPath 링크로 보낼 뿐이다 —
/// 사용자 학번·비밀번호를 수집하지 않는다는 설계 결정의 귀결.
class _ApplyBar extends StatelessWidget {
  const _ApplyBar({required this.url});

  final String url;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
        child: FilledButton.icon(
          icon: const Icon(Icons.open_in_new),
          label: const Text('SSUPath 에서 신청하기'),
          onPressed: url.isEmpty ? null : () => _open(context, url),
        ),
      ),
    );
  }

  Future<void> _open(BuildContext context, String url) async {
    final messenger = ScaffoldMessenger.of(context);
    final uri = Uri.tryParse(url);
    if (uri == null) {
      messenger.showSnackBar(const SnackBar(content: Text('잘못된 링크입니다')));
      return;
    }
    final opened = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!opened) {
      messenger.showSnackBar(const SnackBar(content: Text('링크를 열지 못했습니다')));
    }
  }
}
