import 'package:flutter/material.dart';

/// Linear.app 디자인 시스템 토큰 — 라이트 변형.
///
/// 값의 근거는 저장소 루트 DESIGN.md 에 있다. 바꾸려면 문서를 먼저 고친다 —
/// 문서가 정본이고 코드가 사본이다.
///
/// Linear 원본은 라이트 모드를 지원하지 않는다고 명시한다. 다만 Inverse
/// 토큰(#FFFFFF, #F5F6F6, #F6F7F7, #000000)은 문서화되어 있어 그것을 기준으로
/// 삼았다. 원본에 없는 중간 단계는 파생값이며 각 항목에 표시했다.
abstract final class SsuColors {
  // ── Brand & Accent (다크와 동일) ─────────────────────────────────────────
  /// 희소 자원이다. 브랜드·주요 CTA·포커스 링·찜 활성에만 쓴다.
  static const accent = Color(0xFF5E6AD2);
  static const accentHover = Color(0xFF828FFF);
  static const accentFocus = Color(0xFF5E69D1);

  // ── Surface Ladder (4단계. 건너뛰지 않는다) ─────────────────────────────
  /// 원본 Inverse Canvas
  static const canvas = Color(0xFFFFFFFF);

  /// 원본 Inverse Surface-1
  static const surface1 = Color(0xFFF5F6F6);

  /// 파생 — 원본 Inverse Surface-2(#F6F7F7)는 surface1 과 1단위 차이라
  /// 화면에서 구분되지 않는다. 실제 위계가 보이도록 낮췄다.
  static const surface2 = Color(0xFFEDEEF0);

  /// 파생
  static const surface3 = Color(0xFFE7E8EB);

  /// 파생
  static const surface4 = Color(0xFFE1E2E6);

  // ── Hairlines (파생) ─────────────────────────────────────────────────────
  static const hairline = Color(0xFFE3E4E8);
  static const hairlineStrong = Color(0xFFD2D4DA);
  static const hairlineTertiary = Color(0xFFC4C7CE);

  // ── Ink ──────────────────────────────────────────────────────────────────
  /// 원본 Inverse Ink 는 #000000 이지만, 캔버스를 순수 검정으로 쓰지 않는
  /// 원본 규칙을 뒤집어 적용해 순수 검정 글자도 쓰지 않는다.
  static const ink = Color(0xFF0D0E10);

  static const inkMuted = Color(0xFF3C4149);
  static const inkSubtle = Color(0xFF6B7280);

  /// 비활성, 각주, 종료 공고
  static const inkTertiary = Color(0xFF9CA3AF);

  // ── Status Tags ──────────────────────────────────────────────────────────
  // 색을 면적으로 쓰지 않고 6px 점으로만 쓴다. 배지 배경은 상태와 무관하게
  // 항상 surface2 다. 밝은 배경에서 읽히도록 다크 변형보다 어둡게 잡았다.
  static const tagOpen = Color(0xFF2F80ED);
  static const tagAlways = Color(0xFF1E8E3E);
  static const tagWarning = Color(0xFFD9730D);
  static const tagClosed = Color(0xFF9CA3AF);
}

/// 간격 스케일. Linear 원본 그대로.
abstract final class SsuSpace {
  static const xxs = 4.0;
  static const xs = 8.0;
  static const sm = 12.0;
  static const md = 16.0;
  static const lg = 24.0;
  static const xl = 32.0;
  static const xxl = 48.0;
}

/// 반경 스케일. Linear 원본 그대로.
abstract final class SsuRadius {
  static const xs = 4.0;
  static const sm = 6.0;

  /// 버튼·입력. 주요 버튼을 pill 로 만들지 않는다.
  static const md = 8.0;
  static const lg = 12.0;
  static const xl = 16.0;

  /// 상태 배지, 탭 전용
  static const pill = 9999.0;
}

/// 폰트 패밀리.
///
/// Linear 서체는 독점이라 원본이 허용한 오픈소스 대체를 쓴다.
/// Inter 에는 한글이 없어 Noto Sans KR 을 폴백으로 둔다.
abstract final class SsuFont {
  static const latin = 'Inter';
  static const korean = 'NotoSansKR';

  /// 정원·D-day 등 숫자 강조
  static const mono = 'JetBrainsMono';
}

/// 레이아웃 상수. DESIGN.md 5·8절.
abstract final class SsuLayout {
  /// 태블릿 이하 본문 최대폭
  static const contentWidth = 720.0;

  /// 데스크톱 최대폭
  static const maxWidth = 1280.0;

  /// 2분할 진입 폭
  static const splitBreakpoint = 1024.0;

  /// 터치 타깃 최소 크기
  static const minTouchTarget = 44.0;

  /// 상태 점 지름
  static const statusDot = 6.0;
}
