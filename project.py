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

## Position 열을 기준으로 그룹화하여 Centre-Forward 데이터 추출
grouped_data = df.groupby("Position")  # Position 열 기준 그룹화
cf_group = grouped_data.get_group("Centre-Forward")  # Centre-Forward 데이터 추출

# 그룹화 데이터에 Goals 추가
cf_stats = cf_group[["Name", "Goals", "Goals per Match", "Minutes per goal", "Field Goals", "Rank"]].reset_index(drop=True)

# Goals 기준으로 정렬
cf_stats = cf_stats.sort_values(by="Goals", ascending=False)

# Rank를 index로 설정
cf_stats.set_index("Rank", inplace=True)

# 결과 출력
print(cf_stats)

# 시각화 - 이름과 Goals를 X축으로, 나머지 데이터를 Y축으로 설정
plt.figure(figsize=(12, 5))

# 이름과 Goals를 X축으로 필드골 수 막대그래프
sns.barplot(data=cf_stats, x='Name', y='Field Goals', order=cf_stats['Name'])
plt.title('Field Goals by Centre-Forwards (Sorted by Goals)')
plt.xticks(rotation=45)
plt.xlabel('Player Name')
plt.ylabel('Field Goals')
plt.show()

# 경기당 평균 득점 vs 이름과 Goals
plt.figure(figsize=(12, 6))
sns.barplot(data=cf_stats, x='Name', y='Goals per Match', order=cf_stats['Name'])
plt.title('Goals per Match by Centre-Forwards (Sorted by Goals)')
plt.xticks(rotation=45)
plt.xlabel('Player Name')
plt.ylabel('Goals per Match')
plt.show()

# 득점당 평균 시간 vs 이름과 Goals
plt.figure(figsize=(12, 6))
sns.barplot(data=cf_stats, x='Name', y='Minutes per goal', order=cf_stats['Name'])
plt.title('Minutes per Goal by Centre-Forwards (Sorted by Goals)')
plt.xticks(rotation=45)
plt.xlabel('Player Name')
plt.ylabel('Minutes per Goal')
plt.show()
