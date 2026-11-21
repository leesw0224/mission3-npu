import json
import time

# EPSILON: 부동소수점 오차 허용 임계값 (1e-9)
# 두 필터의 유사도 차이가 EPSILON 미만이면 동점(UNDECIDED)으로 처리
# IEEE 754 부동소수점 연산의 미세한 오차로 인한 오판정을 방지하기 위해 설정
EPSILON = 1e-9


def normalize_label(label: str) -> str:
    """
    라벨 정규화 함수: 다양한 형태의 입력 라벨을 표준 형식으로 변환
    - 'cross', '+' -> 'Cross' (십자 필터)
    - 'x', 'diag'  -> 'X'     (대각 필터)
    대소문자·별칭 등 다양한 입력을 일관된 형식으로 변환하여 정확한 비교를 보장.
    새로운 별칭 추가 시: cleaned in [...] 목록에 추가하면 됩니다.
    """
    cleaned = label.strip().lower()
    if cleaned in ["cross", "+"]:
        return "Cross"
    if cleaned in ["x", "diag", "diagonal"]:
        return "X"
    return label.strip()


def normalize_filter_key(key: str) -> str:
    """
    필터 키 정규화 함수: data.json의 필터 키를 소문자 표준 형식으로 변환
    - 'Cross', 'CROSS', 'cross', '+' -> 'cross'
    - 'X', 'x', 'diagonal', 'diag'  -> 'x'
    data.json 필터 키가 다양한 표기로 작성되어도 올바르게 매칭됩니다.
    """
    cleaned = key.strip().lower()
    if cleaned in ["cross", "+"]:
        return "cross"
    if cleaned in ["x", "diag", "diagonal"]:
        return "x"
    return cleaned


def mac_calculation(matrix_a, matrix_b):
    """
    MAC(Multiply-Accumulate) 연산 구현
    - 순수 파이썬 이중 반복문(for loop)으로 구현 (numpy 등 외부 라이브러리 미사용)
    - 행렬 A와 B의 대응 원소를 곱하고 누적하여 내적(dot product) 값을 반환
    - 시간복잡도: O(N²) - N×N 행렬의 모든 원소(N²개)를 순회하며 곱셈·누적 연산 수행
    - N이 커질수록 연산 횟수가 N²에 비례하여 증가 (3→9, 5→25, 13→169, 25→625)
    """
    total = 0
    rows = len(matrix_a)
    cols = len(matrix_a[0])
    # 이중 반복문: O(N²) 시간복잡도의 핵심 구조
    for r in range(rows):
        for c in range(cols):
            total += matrix_a[r][c] * matrix_b[r][c]  # Multiply-Accumulate
    return total


def benchmark_mac(matrix_a, matrix_b, iterations=10):
    """
    MAC 연산 성능 벤치마크 함수
    - I/O를 제외한 순수 MAC 연산 구간만 time.perf_counter로 측정
    - iterations=10회 반복 측정 후 평균 연산 시간(초)을 반환
    - 10회 반복 평균으로 측정 오차를 최소화
    """
    start_time = time.perf_counter()   # 연산 시작 시각 (I/O 제외)
    res = 0
    for _ in range(iterations):
        res = mac_calculation(matrix_a, matrix_b)
    elapsed = (time.perf_counter() - start_time) / iterations  # 평균 연산 시간(초)
    return res, elapsed


def classify_pattern(pattern_matrix, filter_a, filter_b, label_a="Cross", label_b="X"):
    """
    패턴 분류 함수
    - MAC 연산으로 패턴과 각 필터의 유사도(내적 값)를 계산
    - Cross 유사도 > X 유사도 → 'Cross' 판정
    - X 유사도 > Cross 유사도 → 'X' 판정
    - |유사도 차이| < EPSILON → 'UNDECIDED' 판정 (동점 처리)
    """
    sim_a = mac_calculation(pattern_matrix, filter_a)
    sim_b = mac_calculation(pattern_matrix, filter_b)

    diff = sim_a - sim_b
    if abs(diff) < EPSILON:
        # 부동소수점 오차 기준 동점: UNDECIDED 반환 → FAIL로 집계
        predicted = "UNDECIDED"
    elif diff > 0:
        predicted = label_a  # Cross 유사도가 더 높음
    else:
        predicted = label_b  # X 유사도가 더 높음

    return sim_a, sim_b, predicted


def get_3x3_input(prompt_name):
    """3x3 행렬 입력 함수 (유효하지 않은 입력에 대한 예외 처리 포함)"""
    print(f"\n[{prompt_name}] 3x3 행렬의 각 행을 3개의 숫자(공백 구분)로 입력하세요:")
    matrix = []
    for i in range(3):
        while True:
            try:
                line = input(f"  {i+1}행: ").strip()
                values = [float(x) for x in line.split()]
                if len(values) != 3:
                    print("  [오류] 정확히 3개의 숫자를 공백으로 구분하여 입력해야 합니다.")
                    continue
                matrix.append(values)
                break
            except ValueError:
                print("  [오류] 올바른 숫자를 입력해주세요.")
    return matrix


def run_mode_1():
    """
    모드 1: 사용자 입력 기반 3x3 시뮬레이션
    - 필터 A(Cross), 필터 B(X), 입력 패턴을 직접 입력받아 MAC 연산 수행
    - 10회 반복 측정 평균 연산 시간(ms) 출력
    - EPSILON 기준 동점 처리(UNDECIDED) 포함
    """
    print("\n==========================================")
    print(" 모드 1: 사용자 입력 기반 시뮬레이션 (3x3)")
    print("==========================================")
    filter_a = get_3x3_input("필터 A (Cross)")
    filter_b = get_3x3_input("필터 B (X)")
    pattern = get_3x3_input("입력 패턴")

    # I/O 제외, 순수 MAC 연산 구간만 시간 측정 (10회 반복 평균)
    sim_a, time_a = benchmark_mac(pattern, filter_a, iterations=10)
    sim_b, time_b = benchmark_mac(pattern, filter_b, iterations=10)

    diff = sim_a - sim_b
    if abs(diff) < EPSILON:
        predicted = "UNDECIDED"
    elif diff > 0:
        predicted = "Cross"
    else:
        predicted = "X"

    print("\n---------------- [분석 결과] ----------------")
    print(f"필터 A (Cross) 유사도: {sim_a:.2f} (10회 평균 연산시간: {time_a * 1e3:.4f} ms)")
    print(f"필터 B (X)     유사도: {sim_b:.2f} (10회 평균 연산시간: {time_b * 1e3:.4f} ms)")
    print(f"판정 결과: {predicted}")
    if predicted == "UNDECIDED":
        print("  ※ 유사도 차이가 EPSILON(1e-9) 이하이므로 동점(UNDECIDED)으로 판정되었습니다.")
    print("---------------------------------------------")


# ------------------------------------------------------------
# 실패 원인 진단 (데이터/스키마 문제 vs 로직 문제 vs 수치 비교 문제)
# ------------------------------------------------------------
CAUSE_DATA = "데이터/스키마 문제"
CAUSE_LOGIC = "로직 문제"
CAUSE_NUMERIC = "수치 비교 문제"
REQUIRED_KEYS = ["name", "size", "data", "expected"]


def is_square_matrix(matrix, n):
    """matrix가 숫자로만 이루어진 n x n 2차원 리스트인지 확인"""
    if not isinstance(matrix, list) or len(matrix) != n:
        return False
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            return False
        for v in row:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return False
    return True


def validate_case(p, filters):
    """
    [1단계 진단] 데이터/스키마 검사 - MAC 연산 전에 실행
    - 문제가 있으면 (None, None, 원인 문구) 반환 -> 해당 케이스만 FAIL 처리 후 다음으로 진행
    - 정상이면 (Cross 필터, X 필터, None) 반환
    """
    if not isinstance(p, dict):
        return None, None, "패턴 항목이 객체(dict) 형식이 아님"
    missing = [k for k in REQUIRED_KEYS if k not in p]
    if missing:
        return None, None, f"필수 키 누락: {', '.join(missing)}"

    size = p["size"]
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        return None, None, f"size 값이 양의 정수가 아님: {size!r}"

    if normalize_label(str(p["expected"])) not in ["Cross", "X"]:
        return None, None, f"알 수 없는 기대 라벨: {p['expected']!r}"

    size_key = f"size_{size}"
    if size_key not in filters:
        return None, None, f"'{size_key}' 필터가 data.json에 없음"

    # 필터 키 정규화: 'Cross', 'CROSS', '+', 'X', 'diag' 등을 'cross' / 'x'로 통일
    f_dict = {normalize_filter_key(k): v for k, v in filters[size_key].items()}
    if "cross" not in f_dict or "x" not in f_dict:
        return None, None, f"'{size_key}'에 cross 또는 x 필터가 없음"
    f_cross, f_x = f_dict["cross"], f_dict["x"]

    if not is_square_matrix(p["data"], size):
        return None, None, f"입력 패턴이 {size}x{size} 숫자 배열이 아님 (크기 불일치 또는 숫자 아닌 값)"
    if not is_square_matrix(f_cross, size) or not is_square_matrix(f_x, size):
        return None, None, f"'{size_key}' 필터가 {size}x{size} 숫자 배열이 아님"
    if f_cross == f_x:
        return None, None, f"'{size_key}'의 cross 필터와 x 필터가 완전히 같음 (필터 데이터 오류)"

    return f_cross, f_x, None


def diagnose_failure(expected, predicted, sim_c, sim_x, f_cross, f_x):
    """
    [2단계 진단] 데이터 검사를 통과했는데 FAIL이 난 경우의 원인 분류
    - UNDECIDED + 입력이 두 필터 모양을 모두 꽉 채움 -> 데이터/스키마 문제
      (입력에 Cross와 X가 함께 그려져 있어 어떤 코드로도 구분 불가)
    - UNDECIDED (그 외)  -> 수치 비교 문제 (EPSILON 기준 동점)
    - 그 외 오판정        -> 로직 문제 (점수 차이가 분명한데 기대와 반대로 판정)
    반환값: (분류, 원인 설명, 개선 방향)
    """
    diff = abs(sim_c - sim_x)
    if predicted == "UNDECIDED":
        # 필터 자기 자신과의 MAC 값 = 해당 모양을 완벽히 포함할 때 나올 수 있는 최대 점수
        max_c = mac_calculation(f_cross, f_cross)
        max_x = mac_calculation(f_x, f_x)
        if diff == 0 and sim_c == max_c and sim_x == max_x:
            return (CAUSE_DATA,
                    f"입력이 Cross 모양({sim_c}/{max_c})과 X 모양({sim_x}/{max_x})을 모두 꽉 채움 "
                    "-> 입력 패턴에 두 모양이 함께 들어 있음",
                    "입력 패턴을 기대 라벨 모양 하나만 남도록 수정")
        if diff == 0:
            return (CAUSE_NUMERIC,
                    f"두 점수가 완전히 같음 (Cross={sim_c}, X={sim_x}) -> 오차가 아닌 실제 동점",
                    "입력 패턴이 두 모양의 중간 형태인지 확인")
        return (CAUSE_NUMERIC,
                f"점수 차이 {diff:.1e} < EPSILON({EPSILON}) -> 부동소수점 오차 범위의 동점",
                "EPSILON 정책에 따라 UNDECIDED가 정상 동작 (== 비교를 쓰면 오판정 위험)")
    return (CAUSE_LOGIC,
            f"점수 차이 {diff:.1f}로 분명한데 기대 '{expected}'와 다른 '{predicted}'로 판정",
            "필터 선택(size_N, cross/x 매핑), 비교 조건(>, <), 라벨 정규화 로직 점검")


def run_mode_2(json_path="data.json"):
    """
    모드 2: data.json 자동 로드 및 종합 분석
    [1] 필터 로드 (3x3 ~ 25x25)
    [2] 패턴별 분류 및 PASS/FAIL 검증 (UNDECIDED는 FAIL로 집계)
        - 데이터/스키마 오류 케이스는 연산 없이 FAIL 처리 후 다음 케이스 진행
    [3] 크기별 MAC 연산 성능 분석표 (10회 반복 평균, O(N²) 연산 횟수, ms 단위)
    [4] 결과 요약 + 실패 원인 진단 (데이터/스키마 vs 로직 vs 수치 비교)
    """
    print("\n==========================================")
    print(f" 모드 2: {json_path} 자동 로드 및 종합 분석")
    print("==========================================")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[오류] {json_path} 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as e:
        print(f"[오류] {json_path} JSON 문법 오류: {e}")
        return

    if not isinstance(data, dict):
        print("[오류] JSON 최상위 구조가 객체가 아닙니다. (filters, patterns 키 필요)")
        return
    filters = data.get("filters", {})
    patterns = data.get("patterns", [])
    if not isinstance(filters, dict) or not isinstance(patterns, list):
        print("[오류] filters는 객체, patterns는 리스트 형식이어야 합니다.")
        return

    # [1] 필터 로드 현황
    print("\n[1] 필터 로드 현황:")
    for size_key, f_dict in filters.items():
        size_val = size_key.replace("size_", "")
        names = list(f_dict.keys()) if isinstance(f_dict, dict) else "형식 오류"
        print(f"  - {size_val}x{size_val}: {names}")

    # [2] 패턴별 분류 및 검증
    print("\n[2] 패턴별 분류 및 검증:")
    results = []
    size_stats = {}

    for idx, p in enumerate(patterns, start=1):
        name = p.get("name", f"pattern_{idx}") if isinstance(p, dict) else f"pattern_{idx}"

        # 1단계: 데이터/스키마 검사 (실패해도 프로그램은 종료하지 않음)
        f_cross, f_x, data_error = validate_case(p, filters)
        if data_error:
            results.append({
                "name": name, "pass": False, "cause": CAUSE_DATA,
                "detail": data_error, "fix": "data.json의 해당 항목 수정 후 재실행",
            })
            print(f"  [FAIL] {name}")
            print(f"         {CAUSE_DATA}: {data_error}")
            continue

        size = p["size"]
        expected = normalize_label(str(p["expected"]))  # 라벨 정규화 적용
        p_matrix = p["data"]

        sim_c, sim_x, predicted = classify_pattern(
            p_matrix, f_cross, f_x, label_a="Cross", label_b="X"
        )
        is_pass = (predicted == expected)  # UNDECIDED는 기대값과 다르므로 FAIL
        record = {
            "name": name, "size": size, "expected": expected, "predicted": predicted,
            "sim_cross": sim_c, "sim_x": sim_x, "pass": is_pass,
        }
        if not is_pass:
            # 2단계: 로직 문제 vs 수치 비교 문제 분류
            record["cause"], record["detail"], record["fix"] = diagnose_failure(
                expected, predicted, sim_c, sim_x, f_cross, f_x)
        results.append(record)

        tag = "[PASS]" if is_pass else "[FAIL]"
        print(f"  {tag} {name} (크기: {size}x{size})")
        print(f"         기대 라벨: {expected} | 판정: {predicted} | Cross 유사도: {sim_c:.1f}, X 유사도: {sim_x:.1f}")

        # 크기별 성능 측정 데이터 수집 (I/O 제외, 순수 연산 구간만 측정)
        size_stats.setdefault(size, [])
        _, avg_t = benchmark_mac(p_matrix, f_cross, iterations=10)
        size_stats[size].append(avg_t)

    # [3] 크기별 MAC 연산 성능 분석 (O(N²) 시간복잡도 검증, ms 단위)
    print("\n[3] 크기별 MAC 연산 성능 분석 (10회 반복 측정 평균):")
    print("-" * 58)
    print(f"{'크기':<10}{'MAC 연산 횟수(N²)':<20}{'평균 연산 시간(ms)':<18}")
    print("-" * 58)
    for sz in sorted(size_stats.keys()):
        mac_count = sz * sz  # O(N²): 연산 횟수는 N²에 비례
        avg_time_ms = (sum(size_stats[sz]) / len(size_stats[sz])) * 1e3  # 초 → ms 변환
        print(f"{sz}x{sz:<7}{mac_count:<20}{avg_time_ms:<18.4f}")
    print("-" * 58)

    # [4] 결과 요약
    total_patterns = len(results)
    if total_patterns == 0:
        print("\n[4] 결과 요약: 분석할 패턴이 없습니다.")
        return
    pass_count = sum(1 for r in results if r["pass"])
    fail_count = total_patterns - pass_count
    undecided_count = sum(1 for r in results if r.get("predicted") == "UNDECIDED")

    print("\n[4] 결과 요약:")
    print(f"  - 총 패턴 수: {total_patterns}개")
    print(f"  - 성공 (PASS): {pass_count}개")
    print(f"  - 실패 (FAIL): {fail_count}개 (UNDECIDED {undecided_count}개 포함)")
    print(f"  - 일치율: {(pass_count / total_patterns) * 100:.1f}%")

    if fail_count > 0:
        print("\n  [실패 원인 분류]")
        for cause in [CAUSE_DATA, CAUSE_LOGIC, CAUSE_NUMERIC]:
            cnt = sum(1 for r in results if r.get("cause") == cause)
            print(f"  - {cause}: {cnt}건")

        print("\n  [실패 케이스 진단]")
        for r in results:
            if not r["pass"]:
                print(f"  - {r['name']} -> {r['cause']}")
                print(f"    원인: {r['detail']}")
                print(f"    개선: {r['fix']}")
    else:
        print("\n  실패 0건: 데이터 검사 통과, 모든 판정이 기대 라벨과 일치,")
        print("  EPSILON 범위 동점 없음 -> 세 가지 실패 원인 모두 발생하지 않음")


def main():
    """
    Mini NPU Simulator 메인 함수
    - 모드 1: 사용자 직접 입력 (3x3), 연산 시간 ms 단위 출력
    - 모드 2: data.json 자동 분석 (3x3 ~ 25x25), 크기별 성능표 ms 단위 출력
    - 모드 3: test_failures.json으로 실패 원인 진단 기능 확인
    """
    print("=" * 45)
    print("     Mini NPU Simulator (CS Mission 3)     ")
    print("=" * 45)
    print("1. 사용자 입력 모드 (3x3 수동 입력)")
    print("2. data.json 자동 분석 모드 (3x3 ~ 25x25)")
    print("3. 실패 원인 진단 테스트 (test_failures.json)")
    choice = input("실행할 모드를 선택하세요 (1, 2, 3): ").strip()
    if choice == "1":
        run_mode_1()
    elif choice == "2":
        run_mode_2("data.json")
    elif choice == "3":
        run_mode_2("test_failures.json")
    else:
        print("[오류] 1, 2, 3 중에서 입력해주세요.")


if __name__ == "__main__":
    main()