import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ssunoti_flutter/main.dart';
import 'package:ssunoti_flutter/models/notice.dart';
import 'package:ssunoti_flutter/providers/favorites_provider.dart';
import 'package:ssunoti_flutter/providers/notices_provider.dart';
import 'package:ssunoti_flutter/theme/app_theme.dart';
import 'package:ssunoti_flutter/widgets/notice_card.dart';

/// 셸 레이아웃 회귀 테스트.
///
/// 하단 네비게이션을 `Center` 로 감쌌더니 그 위젯이 화면 세로를 전부 차지해
/// 본문 높이가 0 이 되고 목록이 통째로 사라진 적이 있다.
/// `flutter analyze` 도 provider 단위 테스트도 이걸 잡지 못했다 —
/// 타입은 맞고 상태 로직도 정상이었기 때문이다.
///
/// 그래서 "화면에 실제로 그려지는가"를 확인하는 테스트를 따로 둔다.
void main() {
  Notice makeNotice(String id, String title) => Notice(
        noticeId: id,
        title: title,
        url: 'https://example.invalid/$id',
        content: '테스트 공고 요약',
        deadline: null,
        applicantCount: 3,
        waitlistCount: 0,
        capacity: 30,
        createdAt: DateTime(2026, 7, 30),
      );

  Future<void> pumpShell(WidgetTester tester, List<Notice> notices) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
          // Firestore 를 건드리지 않도록 목록 스트림을 직접 주입한다.
          noticesProvider.overrideWith((ref) => Stream.value(notices)),
        ],
        child: MaterialApp(
          theme: AppTheme.light(),
          home: const HomeShell(),
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  group('HomeShell 레이아웃', () {
    testWidgets('하단 네비게이션이 본문 높이를 잡아먹지 않는다', (tester) async {
      await pumpShell(tester, [makeNotice('a' * 32, '공고 하나')]);

      final scaffold = find.byType(Scaffold).first;
      final navBar = find.byType(NavigationBar);

      expect(navBar, findsOneWidget);

      final scaffoldHeight = tester.getSize(scaffold).height;
      final navHeight = tester.getSize(navBar).height;

      expect(
        navHeight,
        lessThan(scaffoldHeight / 2),
        reason: '하단 네비게이션이 화면 절반 이상을 차지한다. '
            'Center 대신 Align(heightFactor: 1.0) 을 써야 한다.',
      );
    });

    testWidgets('공고 목록이 실제로 그려진다', (tester) async {
      await pumpShell(tester, [
        makeNotice('a' * 32, '첫 번째 공고'),
        makeNotice('b' * 32, '두 번째 공고'),
      ]);

      expect(find.byType(NoticeCard), findsNWidgets(2));
      expect(find.text('첫 번째 공고'), findsOneWidget);
      expect(find.text('두 번째 공고'), findsOneWidget);
    });

    testWidgets('앱바 제목이 보인다', (tester) async {
      await pumpShell(tester, [makeNotice('a' * 32, '공고')]);

      expect(find.text('비교과 공고'), findsOneWidget);
    });

    testWidgets('마감 없는 공고는 상시모집으로 표시된다', (tester) async {
      await pumpShell(tester, [makeNotice('a' * 32, '상시 공고')]);

      // deadline == null 을 "오늘 마감" 으로 표시하면 안 된다.
      expect(find.text('상시모집'), findsOneWidget);
      expect(find.text('오늘 마감'), findsNothing);
    });

    testWidgets('정원이 null 이면 정원 미정으로 표시된다', (tester) async {
      final notice = Notice(
        noticeId: 'c' * 32,
        title: '정원 미상 공고',
        url: 'https://example.invalid/c',
        content: '',
        deadline: null,
        applicantCount: 0,
        waitlistCount: 0,
        capacity: null,
        createdAt: DateTime(2026, 7, 30),
      );

      await pumpShell(tester, [notice]);

      // 0 으로 표시하면 0/0 이 되어 마감으로 읽힌다 — ADR-0003.
      expect(find.text('정원 미정'), findsOneWidget);
      expect(find.text('0/0'), findsNothing);
    });
  });
}
