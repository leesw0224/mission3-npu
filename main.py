
import json
import math

EPSILON = 1e-9


# 1. 메뉴 출력
def show_menu():
    print("\n" + "=" * 40)
    print("       Mini NPU Simulator")
    print("=" * 40)
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("0. 프로그램 종료")
    print("=" * 40)


# 2. 3x3 배열 검증
def validate_matrix(matrix):
    if not isinstance(matrix, list) or len(matrix) != 3:
        return False

    for row in matrix:
        if not isinstance(row, list) or len(row) != 3:
            return False

        for value in row:
            if isinstance(value, bool):
                return False

            if not isinstance(value, (int, float)):
                return False

            if not math.isfinite(value):
                return False

    return True


# 3. MAC 연산
def mac_operation(pattern, filter_data):
    if not validate_matrix(pattern):
        raise ValueError("입력 패턴의 크기가 올바르지 않습니다.")

    if not validate_matrix(filter_data):
        raise ValueError("필터의 크기가 올바르지 않습니다.")

    score = 0

    for i in range(3):
        for j in range(3):
            score += pattern[i][j] * filter_data[i][j]

    return score


# 4. 점수 비교
def compare_scores(score_a, score_b):
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    elif score_a > score_b:
        return "Cross"

    else:
        return "X"


# 5. 사용자 배열 입력
def input_matrix(name):
    print(f"\n[{name} 입력]")

    matrix = []

    for i in range(3):
        while True:
            try:
                values = input(
                    f"{i + 1}번째 행 (숫자 3개): "
                ).split()

                if len(values) != 3:
                    print("숫자 3개를 입력하세요.")
                    continue

                row = [float(v) for v in values]

                if not all(math.isfinite(v) for v in row):
                    print("유효한 숫자를 입력하세요.")
                    continue

                matrix.append(row)
                break

            except ValueError:
                print("숫자만 입력하세요. 다시 입력해 주세요.")

    return matrix


# 6. 사용자 입력 모드
def user_input_mode():
    filter_a = input_matrix("필터 A (Cross)")
    filter_b = input_matrix("필터 B (X)")
    pattern = input_matrix("비교 패턴")

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)

    print("\n[ 사용자 입력 결과 ]")
    print("Cross 점수:", score_a)
    print("X 점수:", score_b)
    print("최종 판정:", compare_scores(score_a, score_b))


# 7. JSON 데이터 분석
def analyze_json():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("JSON 최상위 구조가 올바르지 않습니다.")

        pattern = data["pattern"]
        filters = data["filters"]

        if not validate_matrix(pattern):
            raise ValueError("pattern은 3x3 배열이어야 합니다.")

        if not isinstance(filters, dict):
            raise ValueError("filters 구조가 올바르지 않습니다.")

        filter_a = filters["Cross"]
        filter_b = filters["X"]

        score_a = mac_operation(pattern, filter_a)
        score_b = mac_operation(pattern, filter_b)

        print("\n[ JSON 분석 결과 ]")
        print("Cross 점수:", score_a)
        print("X 점수:", score_b)
        print("최종 판정:", compare_scores(score_a, score_b))

    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")

    except json.JSONDecodeError:
        print("오류: JSON 문법이 올바르지 않습니다.")

    except (KeyError, TypeError, ValueError) as error:
        print("오류:", error)


# 8. 메인 프로그램
def main():
    while True:
        show_menu()

        choice = input("모드를 선택하세요: ").strip()

        try:
            if choice == "1":
                user_input_mode()

            elif choice == "2":
                analyze_json()

            elif choice == "0":
                print("프로그램을 종료합니다.")
                break

            else:
                print("잘못된 선택입니다. 0, 1, 2 중 입력하세요.")

        except (EOFError, KeyboardInterrupt):
            print("\n프로그램을 종료합니다.")
            break


# 9. 프로그램 시작
if __name__ == "__main__":
    main()
