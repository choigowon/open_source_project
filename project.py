import sys # 인코딩
import requests # 웹 크롤링
from bs4 import BeautifulSoup
import pandas as pd # 데이터셋 분석
import seaborn as sns # 데이터 시각화
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8') # 인코딩 설정

url = "https://www.transfermarkt.com/premier-league/torschuetzenliste/wettbewerb/GB1/saison_id/2023/altersklasse/alle/detailpos//plus/1" # 웹 크롤링 주소

headers = { # User-Agent 설정
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers) # HTTP 요청 및 HTML 파싱
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
else:
    print(f"Failed to fetch data: {response.status_code}")
    exit()

table_rows = soup.find_all("tr", {"class": ["odd", "even"]}) # 데이터 테이블 찾기

data = [] # 데이터 수집
for row in table_rows:
    rank = row.find("td", {"class": "zentriert"}).get_text(strip=True)
    name = row.find("td", {"class": "hauptlink"}).get_text(strip=True) # 이름
    position = row.find_all("td")[1].find_all("tr")[1].find_all("td")[0].get_text(strip=True) # 포지션
    appearances = int(row.find_all("td")[8].get_text(strip=True)) # 경기 수
    penalty_kicks = int(row.find_all("td")[10].get_text(strip=True)) # 페널티 킥 수
    minutes_played = float(row.find_all("td")[11].get_text(strip=True).replace("'", "")) # 출전 시간
    minutes_per_goal = int(row.find_all("td")[12].get_text(strip=True).replace("'", "")) # 득점 당 평균 시간
    goals_per_match = float(row.find_all("td")[13].get_text(strip=True)) # 경기 당 평균 득점
    goals = int(row.find_all("td")[14].get_text(strip=True)) # 득점 수
    
    data.append({ # 데이터 리스트에 추가
        "Rank" : rank,
        "Name": name,
        "Position": position,
        "Appearances" : appearances,
        "Penalty kicks" : penalty_kicks,
        "Minutes Played": minutes_played,
        "Minutes per goal" : minutes_per_goal,
        "Goals per Match": goals_per_match,
        "Goals": goals,
        "Field Goals": goals - penalty_kicks
    })

df = pd.DataFrame(data) # DataFrame으로 변환
#df.set_index("Rank", inplace = True) # Rank를 index로 설정

# 포지션별 데이터 그룹화
grouped = df.groupby("Position")

# 통계 분석 및 그래프 그리기
# 각 포지션별로 'Appearances', 'Field Goals', 'Goals', 'Goals per Match'의 통계 분석
stat_columns = ["Appearances", "Field Goals", "Goals", "Goals per Match"]

# 각 포지션별로 통계량 계산
grouped_stats = grouped[stat_columns].agg(['mean', 'median', 'std'])

# 통계량 출력
print(grouped_stats)

# 포지션별 평균값으로 시각화
plt.figure(figsize=(12, 8))

# Appearances, Field Goals, Goals, Goals per Match 그래프 그리기
plt.subplot(2, 2, 1)
sns.barplot(x=grouped_stats.index, y=grouped_stats[("Appearances", "mean")], hue=grouped_stats.index, palette="viridis", legend=False)
plt.title("Average Appearances by Position")
plt.xticks(rotation=45)

plt.subplot(2, 2, 2)
sns.barplot(x=grouped_stats.index, y=grouped_stats[("Field Goals", "mean")], hue=grouped_stats.index, palette="viridis", legend=False)
plt.title("Average Field Goals by Position")
plt.xticks(rotation=45)

plt.subplot(2, 2, 3)
sns.barplot(x=grouped_stats.index, y=grouped_stats[("Goals", "mean")], hue=grouped_stats.index, palette="viridis", legend=False)
plt.title("Average Goals by Position")
plt.xticks(rotation=45)

plt.subplot(2, 2, 4)
sns.barplot(x=grouped_stats.index, y=grouped_stats[("Goals per Match", "mean")], hue=grouped_stats.index, palette="viridis", legend=False)
plt.title("Average Goals per Match by Position")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
