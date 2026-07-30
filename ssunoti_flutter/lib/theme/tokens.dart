import 'package:flutter/material.dart';

/// SSUPath 실제 CSS 에서 추출한 디자인 토큰.
///
/// 값의 근거는 저장소 루트 DESIGN.md 에 있다. 이 파일의 값을 바꾸려면
/// 먼저 DESIGN.md 를 고친다 — 문서가 정본이고 코드가 사본이다.
abstract final class SsuColors {
  // ── Brand ────────────────────────────────────────────────────────────────
  /// 최상위 강조. 원본 `.label_box .col08`
  static const navy = Color(0xFF0E2767);

  /// 보조 강조. 원본 그림자 색의 원본값
  static const teal = Color(0xFF00688F);

  /// 포인트
  static const cyan = Color(0xFF00A4CA);

  // ── Status (pill 라벨 배경. 원본 클래스와 1:1) ──────────────────────────
  /// 모집중. 원본 `.col01`
  static const statusOpen = Color(0xFF0D97FF);

  /// 모집대기. 원본 `.col02`
  static const statusWaiting = Color(0xFF43B5A4);

  /// 일반 분류. 원본 `.col05`
  static const statusNeutral = Color(0xFF747474);

  /// 강조 분류. 원본 `.col08`
  static const statusEmphasis = Color(0xFF0E2767);

  /// 종료. 원본 `.end .label`
  static const statusClosed = Color(0xFFBCBCBC);

  // ── Text ─────────────────────────────────────────────────────────────────
  static const textStrong = Color(0xFF222222);
  static const textBody = Color(0xFF333333);
  static const textMuted = Color(0xFF666666);
  static const textFaint = Color(0xFF999999);

  /// 종료 공고 제목. 원본 `.end .tit`
  static const textDisabled = Color(0xFF949494);

  // ── Surface & Line ───────────────────────────────────────────────────────
  static const surface = Color(0xFFFFFFFF);

  /// 정보 박스. 원본 `.etc_cont`
  static const surfaceSubtle = Color(0xFFFDFDFD);
  static const surfaceAlt = Color(0xFFFAFAFA);

  static const border = Color(0xFFE6E6E6);

  /// 목록 구분선 (dashed)
  static const borderSoft = Color(0xFFE8E8E8);
  static const borderStrong = Color(0xFFE1E5E6);

  // ── Semantic (원본에 없어 신규 정의) ────────────────────────────────────
  /// 마감 임박 · 정원 임박
  static const warning = Color(0xFFE8590C);

  /// 마감됨 · 오류
  static const danger = Color(0xFFC92A2A);

  /// 찜 하트
  static const favorite = Color(0xFFE64980);
}

/// 간격 스케일. 원본 padding/margin 실측값에서 4의 배수만 추림.
abstract final class SsuSpace {
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 12.0;
  static const lg = 16.0;
  static const xl = 20.0;
  static const xxl = 24.0;
}

/// 반경 스케일. 원본 최다값이 3px 이라 거의 각진 인터페이스다.
abstract final class SsuRadius {
  static const sm = 3.0;
  static const md = 5.0;
  static const lg = 10.0;

  /// 상태 라벨 전용
  static const pill = 50.0;
}

/// 그림자. 원본은 거의 쓰지 않고, 쓰는 곳도 극히 얕다.
abstract final class SsuShadow {
  static const none = <BoxShadow>[];

  static const level1 = <BoxShadow>[
    BoxShadow(
      color: Color(0x0D000000), // rgba(0,0,0,0.05)
      blurRadius: 8,
      offset: Offset(0, 3),
    ),
  ];

  static const level2 = <BoxShadow>[
    BoxShadow(
      color: Color(0x0D000000),
      blurRadius: 15,
      spreadRadius: 2,
      offset: Offset(0, 5),
    ),
  ];

  /// Primary 버튼. 회색이 아니라 브랜드 청록이 섞인 그림자다.
  /// 원본 `0 4px 8px rgba(0,104,143,0.24)`
  static const brand = <BoxShadow>[
    BoxShadow(
      color: Color(0x3D00688F),
      blurRadius: 8,
      offset: Offset(0, 4),
    ),
  ];
}

/// 폰트 패밀리.
abstract final class SsuFont {
  /// 본문. 원본이 100/300/400/500/600 을 로드한다.
  static const body = 'NotoSansKR';

  /// 숫자·영문 강조. 원본이 이 용도로만 쓴다.
  static const numeric = 'Poppins';
}

/// 레이아웃 상수.
abstract final class SsuLayout {
  /// 본문 최대폭. 한글 한 줄이 길면 읽기 나쁘다.
  static const maxContentWidth = 600.0;

  /// 터치 타깃 최소 크기.
  static const minTouchTarget = 48.0;

  /// 2분할 레이아웃 진입 폭.
  static const splitBreakpoint = 1024.0;
}
