# 오픈소스 API를 활용한 데이터 수집 및 분석
2024년 2학기 충북대학교 컴퓨터공학과 오픈소스개발프로젝트 기말 프로젝트

본 프로젝트는 데이터 및 주제를 자유롭게 선정하고 아래 단계를 거쳐 해당 데이터를 분석하는 것을 목표로 한다.

⏰ 기간: 2024.11.12 ~ 2024.12.08

### 1. 데이터 수집
자료 출처: https://www.transfermarkt.com/premier-league/torschuetzenliste/wettbewerb/GB1/saison_id/2023/altersklasse/alle/detailpos//plus/1

자료 내용: 23/24 프리미어리그 득점 순위 (필드골)

### 2. 데이터 분석
그룹화 기준: 포지션
포지션별 통계 분석

![image](https://github.com/user-attachments/assets/7292cf5a-a4cc-46aa-8f0b-16f9d0132770)

1번 그래프
: Appearances(경기 횟수), Hours played(출전 시간) 간의 그래프를 통해 얼마나 자주 기용되는지 확인

![image](https://github.com/user-attachments/assets/76386206-9895-4dee-b09e-fa409e6bbc4f)

2번 그래프
: Goals per match(경기 당 평균 득점), Minutes per Goal(득점 당 평균 시간) 간의 그래프를 통해 얼마나 효율적으로 득점하는지 확인

![image](https://github.com/user-attachments/assets/c21a0857-d86d-4784-959f-541fe748736f)

머신러닝

![image](https://github.com/user-attachments/assets/55f41435-6e8c-4262-8dc3-d957e8f6764a)

### 3. 결과 해석 및 응용 방향 설계
선수 성과 예측 시스템: 사용자가 입력한 출전 시간, 포지션, 경기 수 등의 정보를 바탕으로, 선수의 향후 득점 수 또는 경기당 평균 득점을 예측
