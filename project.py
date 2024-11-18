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

# 1. 경기당 평균 득점 기준 그룹화
df["Goals per Match Group"] = pd.cut(
    df["Goals per Match"], 
    bins=[0, 0.5, 1.0, float('inf')], 
    labels=["Low", "Medium", "High"]
)

# 2. 출전 경기 수 기준 그룹화
df["Appearances Group"] = pd.cut(
    df["Appearances"], 
    bins=[0, 10, 20, 30, float('inf')], 
    labels=["Low", "Medium", "High", "Very High"]
)

# 3. 득점 수 기준 그룹화
df["Goals Group"] = pd.cut(
    df["Goals"], 
    bins=[0, 10, 20, float('inf')], 
    labels=["Contender", "Strong Contender", "Top Contender"]
)

# 그룹별 데이터 분석
# 1. Goals per Match Group별 평균 득점
grouped_goals_per_match = df.groupby("Goals per Match Group", observed=True)["Goals"].mean()
print("\nGoals per Match Group별 평균 득점:")
print(grouped_goals_per_match)

# 2. Appearances Group별 총 득점
grouped_appearances = df.groupby("Appearances Group", observed=True)["Goals"].sum()
print("\nAppearances Group별 총 득점:")
print(grouped_appearances)

# 3. Goals Group별 출전 시간 평균
grouped_goals_time = df.groupby("Goals Group", observed=True)["Minutes Played"].mean()
print("\nGoals Group별 평균 출전 시간:")
print(grouped_goals_time)

plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트 설정

# 그래프 1: Goals per Match Group별 평균 득점 (Seaborn 바 차트)
plt.figure(figsize=(10, 6))
sns.barplot(
    x=grouped_goals_per_match.index,
    y=grouped_goals_per_match.values,
    hue=grouped_goals_per_match.index,  # x 변수를 hue로 지정
    palette="viridis",
    dodge=False
)
plt.title("경기당 평균 득점 그룹별 평균 득점")
plt.xlabel("Goals per Match Group")
plt.ylabel("평균 득점")
plt.legend([], [], frameon=False)  # 불필요한 범례 제거
plt.show()

# 그래프 2: Appearances Group별 총 득점 (Matplotlib 바 차트)
plt.figure(figsize=(10, 6))
grouped_appearances.plot(kind="bar", color="teal")
plt.title("출전 경기 수 그룹별 총 득점")
plt.xlabel("Appearances Group")
plt.ylabel("총 득점")
plt.xticks(rotation=0)
plt.show()
