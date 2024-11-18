import requests # 웹 크롤링
from bs4 import BeautifulSoup
import pandas as pd # 데이터셋 분석
import sys # 인코딩
import seaborn as sns # 데이터 시각화
import matplotlib.pyplot as plt

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
    player_name = row.find("td", {"class": "hauptlink"}).get_text(strip=True) # 이름
    position = row.find_all("td")[1].find_all("tr")[1].find_all("td")[0].get_text(strip=True) # 포지션
    appearances = int(row.find_all("td")[8].get_text(strip=True)) # 경기 수
    penalty_kicks = int(row.find_all("td")[10].get_text(strip=True)) # 페널티 킥 수
    minutes_played = float(row.find_all("td")[11].get_text(strip=True).replace("'", "")) # 출전 시간
    minutes_per_goal = int(row.find_all("td")[12].get_text(strip=True).replace("'", "")) # 득점 당 평균 시간
    goals_per_match = float(row.find_all("td")[13].get_text(strip=True)) # 경기 당 평균 득점
    goals = int(row.find_all("td")[14].get_text(strip=True)) # 득점 수
    
    data.append({ # 데이터 리스트에 추가
        "Rank" : rank,
        "Player Name": player_name,
        "Position": position,
        "Appearances" : appearances,
        "Penalty kicks" : penalty_kicks,
        "Minutes Played": minutes_played,
        "Minutes per goal" : minutes_per_goal,
        "Goals per Match": goals_per_match,
        "Goals": goals
    })

df = pd.DataFrame(data) # DataFrame으로 변환
df.set_index("Rank", inplace = True) # Rank를 index로 설정

sys.stdout.reconfigure(encoding='utf-8') # 인코딩 설정
#print(df.head(10))

# 데이터 정보 출력
print("데이터프레임 정보:")
print(df.info())
print("\n기본 통계:")
print(df.describe())

# 포지션별 데이터 그룹화 및 통계 분석
# 1. 포지션별 평균 득점
grouped_position = df.groupby("Position")["Goals"].mean().sort_values(ascending=False)
print("\n포지션별 평균 득점:")
print(grouped_position)

# 2. 포지션별 경기당 평균 득점
grouped_goals_per_match = df.groupby("Position")["Goals per Match"].mean().sort_values(ascending=False)
print("\n포지션별 경기당 평균 득점:")
print(grouped_goals_per_match)

# 3. 포지션별 득점과 출전 시간의 상관관계 분석
grouped_correlation = df.groupby("Position")[["Goals", "Minutes Played"]].corr().iloc[0::2, -1]
print("\n포지션별 득점과 출전 시간의 상관관계:")
print(grouped_correlation)

plt.rcParams['font.family'] = 'Malgun Gothic' # 한글 폰트 설정

# 포지션별 평균 득점 시각화
sns.barplot(
    x=grouped_position.index,
    y=grouped_position.values,
    hue=grouped_position.index,  # x 변수를 hue로 지정
    palette="viridis",
    dodge=False
)
plt.legend([], [], frameon=False)  # 불필요한 범례 제거
plt.title("포지션별 평균 득점")
plt.xlabel("포지션")
plt.ylabel("평균 득점")
plt.xticks(rotation=45)
plt.show()
