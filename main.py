import json
import time

# EPSILON: 부동소수점 오차 허용 임계값 (1e-9)
# 두 필터의 유사도 차이가 EPSILON 미만이면 동점(UNDECIDED)으로 처리
# 이를 통해 부동소수점 연산의 미세한 오차로 인한 오판정을 방지
EPSILON = 1e-9


def normalize_label(label: str) -> str:
    """
    라벨 정규화 함수: 다양한 형태의 입력 라벨을 표준 형식으로 변환
    - 'cross', '+' -> 'Cross' (십자 필터)
    - 'x', 'diag'  -> 'X'     (대각 필터)
    대소문자·별칭 등 다양한 입력을 일관된 형식으로 변환하여 정확한 비교를 보장
    """
    cleaned = label.strip().lower()
    if cleaned in ["cross", "+"]:
        return "Cross"
    if cleaned in ["x", "diag"]:
        return "X"
    return label.strip()


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
    - iterations회 반복 측정 후 평균 연산 시간(초)을 반환
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
    - 10회 반복 측정 평균 연산 시간(µs) 출력
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
    print(f"필터 A (Cross) 유사도: {sim_a:.2f} (10회 평균 연산시간: {time_a * 1e6:.2f} µs)")
    print(f"필터 B (X)     유사도: {sim_b:.2f} (10회 평균 연산시간: {time_b * 1e6:.2f} µs)")
    print(f"판정 결과: {predicted}")
    if predicted == "UNDECIDED":
        print("  ※ 유사도 차이가 EPSILON(1e-9) 이하이므로 동점(UNDECIDED)으로 판정되었습니다.")
    print("---------------------------------------------")


def run_mode_2():
    """
    모드 2: data.json 자동 로드 및 종합 분석
    [1] 필터 로드 (3x3 ~ 25x25)
    [2] 패턴별 분류 및 PASS/FAIL 검증 (UNDECIDED는 FAIL로 집계)
    [3] 크기별 MAC 연산 성능 분석표 (10회 반복 평균, O(N²) 연산 횟수)
    [4] 결과 요약 (총 패턴수, PASS/FAIL 집계, 실패 원인 분석)
    """
    print("\n==========================================")
    print(" 모드 2: data.json 자동 로드 및 종합 분석")
    print("==========================================")
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[오류] data.json 파일을 찾을 수 없습니다.")
        return

    filters = data.get("filters", {})
    patterns = data.get("patterns", [])

    # [1] 필터 로드 현황
    print("\n[1] 필터 로드 현황:")
    for size_key, f_dict in filters.items():
        size_val = size_key.replace("size_", "")
        print(f"  - {size_val}x{size_val}: {list(f_dict.keys())} 필터 준비 완료")

    # [2] 패턴별 분류 및 검증
    print("\n[2] 패턴별 분류 및 검증:")
    results = []
    size_stats = {}

    for p in patterns:
        name = p["name"]
        size = p["size"]                          # data.json에서 패턴 크기 N을 동적으로 추출
        expected_raw = p.get("expected", "UNKNOWN")
        expected = normalize_label(expected_raw)  # 라벨 정규화 적용
        p_matrix = p["data"]

        # 크기 N에 따라 동적으로 필터 선택 (size_3, size_5, size_13, size_25)
        f_cross = filters[f"size_{size}"]["cross"]
        f_x = filters[f"size_{size}"]["x"]

        sim_c, sim_x, predicted = classify_pattern(
            p_matrix, f_cross, f_x, label_a="Cross", label_b="X"
        )

        # UNDECIDED는 기대값과 다르므로 FAIL로 집계
        is_pass = (predicted == expected)
        results.append({
            "name": name, "size": size, "expected": expected,
            "predicted": predicted, "sim_cross": sim_c, "sim_x": sim_x, "pass": is_pass
        })

        tag = "[PASS]" if is_pass else "[FAIL]"
        print(f"  {tag} {name} (크기: {size}x{size})")
        print(f"         기대 라벨: {expected} | 판정: {predicted} | Cross 유사도: {sim_c:.1f}, X 유사도: {sim_x:.1f}")

        # 크기별 성능 측정 데이터 수집 (I/O 제외, 순수 연산 구간만 측정)
        if size not in size_stats:
            size_stats[size] = []
        _, avg_t = benchmark_mac(p_matrix, f_cross, iterations=10)
        size_stats[size].append(avg_t)

    # [3] 크기별 MAC 연산 성능 분석 (O(N²) 시간복잡도 검증)
    print("\n[3] 크기별 MAC 연산 성능 분석 (10회 반복 측정 평균):")
    print("-" * 55)
    print(f"{'크기':<10}{'MAC 연산 횟수(N²)':<20}{'평균 연산 시간(µs)':<18}")
    print("-" * 55)
    for sz in sorted(size_stats.keys()):
        mac_count = sz * sz  # O(N²): 연산 횟수는 N²에 비례
        avg_time_us = (sum(size_stats[sz]) / len(size_stats[sz])) * 1e6
        print(f"{sz}x{sz:<7}{mac_count:<20}{avg_time_us:<18.2f}")
    print("-" * 55)

    # [4] 결과 요약
    total_patterns = len(results)
    pass_count = sum(1 for r in results if r["pass"])
    fail_count = total_patterns - pass_count  # UNDECIDED 포함 FAIL 집계

    print("\n[4] 결과 요약:")
    print(f"  - 총 패턴 수: {total_patterns}개")
    print(f"  - 성공 (PASS): {pass_count}개")
    print(f"  - 실패 (FAIL): {fail_count}개 (UNDECIDED 포함)")
    print(f"  - 일치율: {(pass_count / total_patterns) * 100:.1f}%")

    if fail_count > 0:
        print("\n  [실패 케이스 원인 분석]")
        for r in results:
            if not r["pass"]:
                print(f"  - {r['name']}: 기대값 '{r['expected']}'이나 실제 판정은 '{r['predicted']}'")
                print(f"    Cross 유사도={r['sim_cross']}, X 유사도={r['sim_x']}")
                if r["predicted"] == "UNDECIDED":
                    print("    -> 원인: 두 필터의 유사도가 동일(동점)하여 EPSILON 기준 UNDECIDED 처리")
                    print("             노이즈 또는 대칭 패턴으로 인해 Cross·X 특징이 동시에 검출됨")


def main():
    """
    Mini NPU Simulator 메인 함수
    - 모드 1: 사용자 직접 입력 (3x3)
    - 모드 2: data.json 자동 분석 (3x3 ~ 25x25)
    """
    print("=" * 45)
    print("     Mini NPU Simulator (CS Mission 3)     ")
    print("=" * 45)
    print("1. 사용자 입력 모드 (3x3 수동 입력)")
    print("2. data.json 자동 분석 모드 (3x3 ~ 25x25)")
    choice = input("실행할 모드를 선택하세요 (1 또는 2): ").strip()
    if choice == "1":
        run_mode_1()
    elif choice == "2":
        run_mode_2()
    else:
        print("[오류] 1 또는 2를 입력해주세요.")


if __name__ == "__main__":
    main()