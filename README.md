# Mini NPU Simulator

## 1. 프로젝트 소개

Python을 활용하여 간단한 NPU(Neural Processing Unit) 연산 과정을 시뮬레이션하는 프로젝트입니다.

3×3 입력 데이터와 필터를 이용하여 MAC(Multiply-Accumulate) 연산을 수행하고, 연산 결과를 비교합니다.

## 2. 주요 기능

### ① 사용자 입력 모드
- 3×3 행렬 데이터 입력
- Cross 필터 연산
- X 필터 연산
- 연산 결과 출력
- 최종 판정 결과 출력

### ② JSON 데이터 분석 모드
- data.json 파일 읽기
- JSON에 저장된 필터 데이터 활용
- Cross 및 X 연산 결과 비교
- 최종 판정 결과 출력

### ③ 프로그램 종료
- 메뉴에서 0을 선택하면 프로그램 종료

## 3. 사용 기술

- Python 3
- JSON
- Git
- GitHub

## 4. 파일 구성

| 파일명 | 설명 |
|---|---|
| main.py | NPU 시뮬레이터 실행 코드 |
| data.json | 입력 패턴 및 필터 데이터 |

## 5. 실행 방법

터미널에서 다음 명령어를 실행합니다.

```bash
python3 main.py
```

## 6. 실행 메뉴

```text
Mini NPU Simulator

1. 사용자 입력 (3x3)
2. data.json 분석
0. 프로그램 종료
```

## 7. 연산 결과 예시

```text
Cross 점수: 5
X 점수: 1
최종 판정: Cross
```

## 8. 프로젝트 목적

행렬 연산과 MAC 연산의 기본 원리를 이해하고, Python을 이용하여 간단한 NPU 연산 과정을 구현하는 것을 목표로 합니다.
