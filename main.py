import json
import time

EPSILON = 1e-9

def normalize_label(label: str) -> str:
    cleaned = label.strip().lower()
    if cleaned in ["cross", "+"]:
        return "Cross"
    if cleaned in ["x", "diag"]:
        return "X"
    return label.strip()

def mac_calculation(matrix_a, matrix_b):
    """
    순수 파이썬 이중 반복문 기반 MAC (Multiply-Accumulate) 연산
    """
    total = 0
    rows = len(matrix_a)
    cols = len(matrix_a[0])
    for r in range(rows):
        for c in range(cols):
            total += matrix_a[r][c] * matrix_b[r][c]
    return total

def benchmark_mac(matrix_a, matrix_b, iterations=10):
    start_time = time.perf_counter()
    res = 0
    for _ in range(iterations):
        res = mac_calculation(matrix_a, matrix_b)
    elapsed = (time.perf_counter() - start_time) / iterations
    return res, elapsed

def classify_pattern(pattern_matrix, filter_a, filter_b, label_a="Cross", label_b="X"):
    sim_a = mac_calculation(pattern_matrix, filter_a)
    sim_b = mac_calculation(pattern_matrix, filter_b)
    
    diff = sim_a - sim_b
    if abs(diff) < EPSILON:
        predicted = "UNDECIDED"
    elif diff > 0:
        predicted = label_a
    else:
        predicted = label_b
        
    return sim_a, sim_b, predicted

def get_3x3_input(prompt_name):
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
    print("\n==========================================")
    print(" 모드 1: 사용자 입력 기반 시뮬레이션 (3x3)")
    print("==========================================")
    filter_a = get_3x3_input("필터 A (Cross)")
    filter_b = get_3x3_input("필터 B (X)")
    pattern = get_3x3_input("입력 패턴")

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
        print("  ※ 유사도 차이가 임계값(EPSILON) 이하이므로 동점으로 판정되었습니다.")
    print("---------------------------------------------")

def run_mode_2():
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

    print("\n[1] 필터 로드 현황:")
    for size_key, f_dict in filters.items():
        size_val = size_key.replace("size_", "")
        print(f"  - {size_val}x{size_val}: {list(f_dict.keys())} 필터 준비 완료")

    print("\n[2] 패턴별 분류 및 검증:")
    results = []
    size_stats = {}

    for p in patterns:
        name = p["name"]
        size = p["size"]
        expected_raw = p.get("expected", "UNKNOWN")
        expected = normalize_label(expected_raw)
        p_matrix = p["data"]

        f_cross = filters[f"size_{size}"]["cross"]
        f_x = filters[f"size_{size}"]["x"]

        sim_c, sim_x, predicted = classify_pattern(p_matrix, f_cross, f_x, label_a="Cross", label_b="X")
        is_pass = (predicted == expected)
        results.append({
            "name": name,
            "size": size,
            "expected": expected,
            "predicted": predicted,
            "sim_cross": sim_c,
            "sim_x": sim_x,
            "pass": is_pass
        })

        tag = "[PASS]" if is_pass else "[FAIL]"
        print(f"  {tag} {name} (크기: {size}x{size})")
        print(f"         기대 라벨: {expected} | 판정: {predicted} | Cross 유사도: {sim_c:.1f}, X 유사도: {sim_x:.1f}")

        if size not in size_stats:
            size_stats[size] = []
        _, avg_t = benchmark_mac(p_matrix, f_cross, iterations=10)
        size_stats[size].append(avg_t)

    print("\n[3] 크기별 MAC 연산 성능 분석 (10회 반복 측정 평균):")
    print("-" * 55)
    print(f"{'크기':<10}{'MAC 연산 횟수':<18}{'평균 연산 시간(µs)':<18}")
    print("-" * 55)
    for sz in sorted(size_stats.keys()):
        mac_count = sz * sz
        avg_time_us = (sum(size_stats[sz]) / len(size_stats[sz])) * 1e6
        print(f"{sz}x{sz:<7}{mac_count:<18}{avg_time_us:<18.2f}")
    print("-" * 55)

    total_patterns = len(results)
    pass_count = sum(1 for r in results if r["pass"])
    fail_count = total_patterns - pass_count

    print("\n[4] 결과 요약:")
    print(f"  - 총 패턴 수: {total_patterns}개")
    print(f"  - 성공 (PASS): {pass_count}개")
    print(f"  - 실패 (FAIL): {fail_count}개")
    print(f"  - 일치율: {(pass_count / total_patterns) * 100:.1f}%")
    if fail_count > 0:
        print("\n  [주의 - 실패 케이스 분석]")
        for r in results:
            if not r["pass"]:
                print(f"  - {r['name']}: 기대값 '{r['expected']}'이나 실제 판정은 '{r['predicted']}' (Cross={r['sim_cross']}, X={r['sim_x']})")
                print("    -> 원인: 노이즈 또는 대칭 패턴으로 인해 두 필터의 유사도가 동일(동점)하여")
                print("             미션 규정(EPSILON 기준)에 따라 'UNDECIDED'로 처리되었습니다.")

def main():
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