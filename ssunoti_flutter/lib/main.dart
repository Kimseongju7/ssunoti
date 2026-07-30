import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'firebase_options.dart';
import 'providers/favorites_provider.dart';
import 'screens/favorites_screen.dart';
import 'screens/notice_list_screen.dart';
import 'services/fcm_service.dart';
import 'theme/app_theme.dart';
import 'theme/tokens.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // 찜 목록은 첫 프레임 전에 읽어야 한다. 나중에 읽으면 하트가 빈 상태로
  // 한 번 그려졌다가 채워져 깜빡인다.
  final prefs = await SharedPreferences.getInstance();

  // 알림은 부가 기능이다. 실패해도 앱은 그대로 뜬다.
  _fireAndForget(FcmService(FirebaseMessaging.instance).initialize());

  runApp(
    ProviderScope(
      overrides: [sharedPreferencesProvider.overrideWithValue(prefs)],
      child: const SsunotiApp(),
    ),
  );
}

/// 결과를 기다리지 않고 실행하되, 실패를 조용히 삼키지는 않는다.
void _fireAndForget(Future<void> future) {
  future.catchError((Object error) {
    debugPrint('[main] 백그라운드 작업 실패: $error');
  });
}

class SsunotiApp extends StatelessWidget {
  const SsunotiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SSUNoti',
      debugShowCheckedModeBanner: false,
      // 테마 값의 근거는 저장소 루트 DESIGN.md 에 있다.
      // 다크 전용이다 — 라이트 모드를 만들지 않는다.
      theme: AppTheme.dark(),
      home: const HomeShell(),
    );
  }
}

/// 공고 목록 / 찜 두 탭.
class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  static const _titles = ['비교과 공고', '찜한 공고'];
  static const _screens = [NoticeListScreen(), FavoritesScreen()];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SsuColors.canvas,
      appBar: AppBar(
        // 제목도 본문과 같은 축에 둔다. 본문만 가운데 정렬하면 축이 둘이 된다.
        title: _Centered(child: Text(_titles[_index])),
        titleSpacing: 0,
      ),
      body: _Centered(
        child: IndexedStack(index: _index, children: _screens),
      ),
      bottomNavigationBar: DecoratedBox(
        decoration: const BoxDecoration(
          color: SsuColors.surface3,
          border: Border(top: BorderSide(color: SsuColors.hairline)),
        ),
        child: SafeArea(
          top: false,
          child: _Centered(
            child: NavigationBar(
              selectedIndex: _index,
              onDestinationSelected: (i) => setState(() => _index = i),
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.list_alt_outlined),
                  selectedIcon: Icon(Icons.list_alt),
                  label: '공고',
                ),
                NavigationDestination(
                  icon: Icon(Icons.favorite_border),
                  selectedIcon: Icon(Icons.favorite),
                  label: '찜',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// 앱바·본문·하단 네비게이션을 같은 폭 축에 묶는다.
///
/// 본문에만 폭 제약을 걸면 넓은 화면에서 축이 둘로 갈린다 —
/// 제목은 왼쪽 끝, 목록은 가운데, 네비게이션은 전체 폭으로 퍼진다.
class _Centered extends StatelessWidget {
  const _Centered({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: SsuLayout.contentWidth),
        child: child,
      ),
    );
  }
}
