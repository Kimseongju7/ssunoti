import 'package:flutter/material.dart';

/// Linear.app 디자인 시스템 토큰.
///
/// 값의 근거는 저장소 루트 DESIGN.md 에 있다. 바꾸려면 문서를 먼저 고친다 —
/// 문서가 정본이고 코드가 사본이다.
abstract final class SsuColors {
  // ── Brand & Accent ───────────────────────────────────────────────────────
  /// 희소 자원이다. 브랜드·주요 CTA·포커스 링·찜 활성에만 쓴다.
  static const accent = Color(0xFF5E6AD2);
  static const accentHover = Color(0xFF828FFF);
  static const accentFocus = Color(0xFF5E69D1);

  // ── Surface Ladder (4단계. 건너뛰지 않는다) ─────────────────────────────
  /// 순수 검정이 아니다. 옅은 청색 기운이 의도된 것.
  static const canvas = Color(0xFF010102);
  static const surface1 = Color(0xFF0F1011);
  static const surface2 = Color(0xFF141516);
  static const surface3 = Color(0xFF18191A);
  static const surface4 = Color(0xFF191A1B);

  // ── Hairlines ────────────────────────────────────────────────────────────
  static const hairline = Color(0xFF23252A);
  static const hairlineStrong = Color(0xFF34343A);
  static const hairlineTertiary = Color(0xFF3E3E44);

  // ── Ink ──────────────────────────────────────────────────────────────────
  static const ink = Color(0xFFF7F8F8);
  static const inkMuted = Color(0xFFD0D6E0);
  static const inkSubtle = Color(0xFF8A8F98);

  /// 비활성, 각주, 종료 공고
  static const inkTertiary = Color(0xFF62666D);

  // ── Status Tags ──────────────────────────────────────────────────────────
  // Linear 마케팅 규칙은 2차 색상을 금지하지만, 원본이 명시하듯 제품 UI 의
  // 상태 태그는 예외다. 대신 색을 면적으로 쓰지 않고 6px 점으로만 쓴다.
  // 배지 배경은 상태와 무관하게 항상 surface2 다.
  static const tagOpen = Color(0xFF4EA7FC);
  static const tagAlways = Color(0xFF27A644);
  static const tagWarning = Color(0xFFF2994A);
  static const tagClosed = Color(0xFF62666D);
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
