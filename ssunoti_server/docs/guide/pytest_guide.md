# pytest 사용 가이드

## 개요

pytest는 Python의 테스트 프레임워크로, 간결한 문법과 강력한 기능을 제공합니다.

---

## 설치

```bash
pip install pytest
```

---

## 기본 사용법

### 1. 테스트 파일 구조

```
tests/
├── __init__.py
├── test_module1.py
├── test_module2.py
└── conftest.py         # 공통 fixture 정의
```

### 2. 테스트 작성 규칙

- 파일명: `test_*.py` 또는 `*_test.py`
- 함수명: `test_`로 시작
- 클래스명: `Test`로 시작

```python
# tests/test_example.py

def test_addition():
    assert 1 + 1 == 2

class TestCalculator:
    def test_subtract(self):
        assert 5 - 3 == 2
```

---

## 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 디렉토리
pytest tests/

# 특정 파일
pytest tests/test_example.py

# 특정 함수
pytest tests/test_example.py::test_addition

# 특정 클래스
pytest tests/test_example.py::TestCalculator

# 특정 클래스의 메서드
pytest tests/test_example.py::TestCalculator::test_subtract

# 키워드로 필터링 (-k)
pytest -k "add"           # 이름에 "add" 포함된 테스트만
pytest -k "not slow"      # "slow" 제외
```

---

## 출력 옵션

```bash
# 상세 출력
pytest -v

# 더 상세한 출력
pytest -vv

# 간략 출력 (점으로 표시)
pytest -q

# print() 출력 보기
pytest -s

# 첫 번째 실패에서 중단
pytest -x

# N개 실패 후 중단
pytest --maxfail=3

# 마지막 실패한 테스트만 재실행
pytest --lf

# 실패한 테스트 먼저 실행
pytest --ff
```

---

## Assert 문

pytest는 기본 `assert` 문을 사용하며, 실패 시 상세한 정보를 제공합니다.

```python
def test_assertions():
    # 동등 비교
    assert 1 + 1 == 2

    # 불일치
    assert 1 + 1 != 3

    # 포함 여부
    assert "hello" in "hello world"
    assert 3 in [1, 2, 3]

    # 참/거짓
    assert True
    assert not False

    # None 체크
    assert None is None
    assert "value" is not None

    # 타입 체크
    assert isinstance("hello", str)

    # 길이
    assert len([1, 2, 3]) == 3

    # 비교
    assert 5 > 3
    assert 3 <= 3
```

---

## Fixture

테스트에 필요한 데이터나 객체를 제공하는 함수입니다.

### 기본 Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "test", "value": 42}

def test_with_fixture(sample_data):
    assert sample_data["name"] == "test"
    assert sample_data["value"] == 42
```

### Fixture Scope

```python
@pytest.fixture(scope="function")  # 기본값: 매 테스트마다 실행
def func_fixture():
    return "function"

@pytest.fixture(scope="class")     # 클래스당 한 번
def class_fixture():
    return "class"

@pytest.fixture(scope="module")    # 모듈당 한 번
def module_fixture():
    return "module"

@pytest.fixture(scope="session")   # 세션당 한 번
def session_fixture():
    return "session"
```

### Setup / Teardown

```python
@pytest.fixture
def database():
    # Setup: 테스트 전 실행
    db = create_connection()

    yield db  # 테스트에 db 전달

    # Teardown: 테스트 후 실행
    db.close()

def test_query(database):
    result = database.query("SELECT 1")
    assert result == 1
```

### conftest.py

여러 테스트 파일에서 공유할 fixture를 정의합니다.

```python
# tests/conftest.py

import pytest
from src import Browser


@pytest.fixture
def browser():
    b = Browser(headless=True)
    yield b
    b.close()
```

---

## 예외 테스트

```python
import pytest

def test_exception():
    with pytest.raises(ValueError):
        raise ValueError("에러 발생")

def test_exception_message():
    with pytest.raises(ValueError, match="에러"):
        raise ValueError("에러 발생")

def test_exception_info():
    with pytest.raises(ZeroDivisionError) as exc_info:
        1 / 0
    assert "division by zero" in str(exc_info.value)
```

---

## 파라미터화

동일한 테스트를 여러 입력값으로 실행합니다.

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected

@pytest.mark.parametrize("a,b,result", [
    (1, 2, 3),
    (5, 5, 10),
    (-1, 1, 0),
])
def test_add(a, b, result):
    assert a + b == result
```

---

## 마커 (Markers)

테스트를 분류하고 선택적으로 실행합니다.

### 내장 마커

```python
import pytest

@pytest.mark.skip(reason="아직 구현 안됨")
def test_not_implemented():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Python 3.10+ 필요")
def test_python310_feature():
    pass

@pytest.mark.xfail(reason="알려진 버그")
def test_known_bug():
    assert False  # 실패해도 전체 테스트는 통과
```

### 커스텀 마커

```python
# pytest.ini
[pytest]
markers =
    slow: 느린 테스트
    integration: 통합 테스트

# test_example.py
import pytest

@pytest.mark.slow
def test_slow_operation():
    time.sleep(10)

@pytest.mark.integration
def test_database_connection():
    pass
```

```bash
# 마커로 필터링
pytest -m slow           # slow 마커만
pytest -m "not slow"     # slow 제외
pytest -m "slow or integration"
```

---

## Mock과 Patch

외부 의존성을 대체합니다.

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    mock_obj = Mock()
    mock_obj.method.return_value = 42

    assert mock_obj.method() == 42
    mock_obj.method.assert_called_once()

@patch('module.external_api')
def test_with_patch(mock_api):
    mock_api.return_value = {"status": "ok"}

    result = call_external_api()
    assert result["status"] == "ok"

def test_patch_context():
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        assert os.path.exists('/fake/path') == True
```

---

## 커버리지

```bash
# pytest-cov 설치
pip install pytest-cov

# 커버리지 측정
pytest --cov=src tests/

# HTML 리포트 생성
pytest --cov=src --cov-report=html tests/

# 특정 커버리지 이하면 실패
pytest --cov=src --cov-fail-under=80 tests/
```

---

## pytest-watch (자동 실행)

```bash
# 설치
pip install pytest-watch

# 파일 변경 감시
ptw

# 특정 디렉토리 감시
ptw tests/

# 옵션 추가
ptw -- -v --lf
```

---

## pytest.ini 설정

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: 느린 테스트
    integration: 통합 테스트
filterwarnings =
    ignore::DeprecationWarning
```

---

## 유용한 플러그인

| 플러그인 | 용도 |
|----------|------|
| `pytest-cov` | 코드 커버리지 |
| `pytest-watch` | 파일 변경 감시 자동 실행 |
| `pytest-xdist` | 병렬 테스트 실행 |
| `pytest-mock` | Mock 헬퍼 |
| `pytest-timeout` | 테스트 타임아웃 설정 |
| `pytest-randomly` | 테스트 순서 무작위화 |
| `pytest-html` | HTML 리포트 생성 |

---

## TDD 워크플로우

```bash
# 1. 터미널에서 pytest-watch 실행
ptw tests/ -- -v

# 2. 실패하는 테스트 작성 (Red)
# tests/test_feature.py
def test_new_feature():
    result = new_function()
    assert result == expected

# 3. 테스트 통과하는 코드 작성 (Green)
# src/module.py
def new_function():
    return expected

# 4. 리팩토링 (Refactor)
# 테스트가 계속 통과하는지 확인하며 코드 개선
```