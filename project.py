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
        "Minutes played": round(minutes_played * 1000 / 60, 1), # 시간 단위
        "Minutes per goal" : minutes_per_goal,
        "Goals per match": goals_per_match,
        "Field goals": goals - penalty_kicks
    })

df = pd.DataFrame(data) # DataFrame으로 변환
#df.set_index("Rank", inplace = True) # Rank를 index로 설정

# 포지션별 데이터 그룹화 후 간단한 통계 분석
grouped = df.groupby("Position")
position_stats = ["Rank", "Name", "Appearances", "Minutes played", "Minutes per goal", "Goals per Match", "Field Goals"]

top_5_by_position = grouped.apply(
    lambda x: x.nlargest(5, ['Appearances', 'Minutes played'])
).reset_index(drop=True)

# 이름 길이 제한 (보기 좋게)
top_5_by_position['Name'] = top_5_by_position['Name'].str.slice(0, 15)

# 데이터 정렬
top_5_by_position = top_5_by_position.sort_values(by='Appearances', ascending=False)

# 그래프 생성
fig, ax = plt.subplots(figsize=(8, 6))  # 그래프 크기 조정

# Minutes played 막대 그래프 (포지션별 색상)
sns.barplot(
    data=top_5_by_position,
    y='Name',  # y축: 선수 이름
    x='Minutes played',  # x축: 출전 시간
    hue='Position',  # 포지션별 색상 구분
    dodge=False,
    alpha=0.7,  # 투명도 설정
    ax=ax
)

# Appearances 막대 그래프 (검은색, 투명도 조정)
sns.barplot(
    data=top_5_by_position,
    y='Name',  # y축: 선수 이름
    x='Appearances',  # x축: 경기 수
    color='black',  # 막대 색상
    alpha=0.3,  # 투명도 설정
    ax=ax
)

# 축 및 레이블 설정
ax.set_title('Minutes Played and Appearances by Top Players', fontsize=14)
ax.set_xlabel('Value', fontsize=12)
ax.set_ylabel('Player Name', fontsize=12)

# 범례 표시
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')

# 레이아웃 조정 및 출력
plt.tight_layout()
plt.show()

# 포지션별로 필드골이 가장 많은 상위 10명의 선수 추출
top_10_field_goals_by_position = grouped.apply(
    lambda x: x.nlargest(10, 'Field goals')
).reset_index(drop=True)

# 시각화 2: 각 포지션에 대한 필드 골과 득점 당 평균 시간 (산점도)
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Field goals', y='Minutes per goal', hue='Position', data=top_10_field_goals_by_position, palette="Set2", s=100)

# 선수 이름 추가
for i in range(top_10_field_goals_by_position.shape[0]):
    plt.text(
        top_10_field_goals_by_position['Field goals'].iloc[i], 
        top_10_field_goals_by_position['Minutes per goal'].iloc[i], 
        top_10_field_goals_by_position['Name'].iloc[i], 
        fontsize=9, ha='right', va='bottom'
    )

plt.title("Field Goals vs Minutes per Goal by Position (Top 10 Players)")
plt.xlabel("Field Goals")
plt.ylabel("Minutes per Goal")
plt.legend(title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# 추가 분석: 각 포지션별로 효율성 지표 관계 분석 (Pairplot)
# Pairplot: 그래프 크기 추가 줄이기
sns.pairplot(
    top_10_field_goals_by_position,
    vars=['Minutes per goal', 'Goals per match', 'Field goals'],  # 분석할 컬럼
    hue='Position',  # 포지션별 색상 구분
    palette="Set2",  # 색상 팔레트
    diag_kind="kde",  # 대각선에 KDE (밀도 그래프)
    height=2  # 그래프 크기 더 줄이기
)

# 제목 위치 및 크기 조정
plt.suptitle("Pairplot of Efficiency Metrics by Position (Top 10 Players)", y=1, fontsize=12)  # 제목 위치 내리기
plt.tight_layout()  # 레이아웃 조정
plt.subplots_adjust(top=0.9, right=0.85)  # 제목 위치를 내리고, 오른쪽 여백을 늘림
plt.show()
