import sys # 인코딩
import requests # 웹 크롤링
from bs4 import BeautifulSoup
import pandas as pd # 데이터셋 분석
import seaborn as sns # 데이터 시각화
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8') # 인코딩 설정

url = "https://www.transfermarkt.com/premier-league/torschuetzenliste/wettbewerb/GB1/plus/1?saison_id=2023&detailpos=&altersklasse=alle&exclude_penalties=1" # 주소
headers = { # User-Agent 설정
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers) # HTTP 요청 및 HTML 파싱
soup = BeautifulSoup(response.text, 'lxml')

table_rows = soup.find_all("tr", {"class": ["odd", "even"]}) # 데이터 테이블 찾기
data = [] # 데이터 수집
for row in table_rows:
    rank = row.find("td", {"class": "zentriert"}).get_text(strip=True) # 순위
    name = row.find("td", {"class": "hauptlink"}).get_text(strip=True) # 이름
    position = row.find_all("td")[1].find_all("tr")[1].find_all("td")[0].get_text(strip=True) # 포지션
    appearances = int(row.find_all("td")[8].get_text(strip=True)) # 경기 수
    minutes_played = float(row.find_all("td")[11].get_text(strip=True).replace("'", "")) # 출전 시간
    minutes_per_goal = int(row.find_all("td")[12].get_text(strip=True).replace("'", "")) # 득점 당 평균 시간
    goals_per_match = float(row.find_all("td")[13].get_text(strip=True)) # 경기 당 평균 득점
    goals = int(row.find_all("td")[14].get_text(strip=True)) # 득점 수
    
    data.append({ # 데이터 리스트에 추가
        "Rank" : rank,
        "Name": name,
        "Position": position,
        "Appearances" : appearances,
        "Hours played": round(minutes_played / 60 * (1000 if minutes_played < 10 else 1), 1), # 시 단위로 변경
        "Minutes per goal" : minutes_per_goal,
        "Goals per match": goals_per_match,
        "Goals" : goals
    })

df = pd.DataFrame(data) # DataFrame으로 변환

tb = df.set_index("Rank") # Rank를 index로 설정
pd.set_option('display.max_columns', 7) # 출력할 열의 개수 설정
print(tb) # 데이터셋 출력

grouped = df.groupby("Position") # 포지션별 데이터 그룹화

position_stats = grouped.agg({ # 포지션별 통계량 계산
    'Hours played': ['mean', 'std'],
    'Appearances': ['mean', 'std'],
    'Minutes per goal': ['mean', 'std'],
    'Goals per match': ['mean', 'std']
}).reset_index()

position_stats.columns = ['Position', 
                          'Avg Hours Played', 'Std Hours Played', 
                          'Avg Appearances', 'Std Appearances', 
                          'Avg Minutes per Goal', 'Std Minutes per Goal', 
                          'Avg Goals per Match', 'Std Goals per Match']

for _, row in position_stats.iterrows(): # 통계량 출력
    print(f"\nPosition: {row['Position']}")
    print(f" - Avg Hours Played: {row['Avg Hours Played']:.1f} ± {row['Std Hours Played']:.1f}")
    print(f" - Avg Appearances: {row['Avg Appearances']:.1f} ± {row['Std Appearances']:.1f}")
    print(f" - Avg Minutes per Goal: {row['Avg Minutes per Goal']:.1f} ± {row['Std Minutes per Goal']:.1f}")
    print(f" - Avg Goals per Match: {row['Avg Goals per Match']:.2f} ± {row['Std Goals per Match']:.2f}")

# 통계량 박스플롯으로 출력
fig, axes = plt.subplots(2, 2, figsize=(12, 6))
fig.suptitle("Distribution of Metrics by Position", fontsize=16)

sns.boxplot(data=df, x="Position", y="Hours played", hue="Position", palette="Set3", ax=axes[0, 0])
sns.boxplot(data=df, x="Position", y="Appearances", hue="Position", palette="Set3", ax=axes[0, 1])
sns.boxplot(data=df, x="Position", y="Minutes per goal", hue="Position", palette="Set3", ax=axes[1, 0])
sns.boxplot(data=df, x="Position", y="Goals per match", hue="Position", palette="Set3", ax=axes[1, 1])

plt.tight_layout()
plt.show()

# 그래프 1: 선수 출전 시간과 경기 수 (막대 그래프)
df['Name'] = df['Rank'].astype(str) + ' ' + df['Name']  # Rank와 Name 동시 출력을 위한 결합
df_sorted = df.sort_values(by='Hours played', ascending=False)  # Appearances 순으로 내림차순 정렬
fig, ax = plt.subplots(figsize=(10, 6))  # 그래프 객체 생성

sns.barplot( # Hours played (출전 시간) 막대 그래프
    x='Hours played', y='Name', hue='Position', dodge=False, data=df_sorted, ax=ax, alpha=0.7
)

sns.barplot( # Appearances (출전 경기 수) 막대 그래프
    x='Appearances', y='Name', data=df_sorted, ax=ax, color='black', alpha=0.3
)

ax.set_title('Hours played and Appearances', fontsize=14) # 제목

handles, labels = ax.get_legend_handles_labels() # 기본 범례
custom_handles = handles + [ # 범례 추가
    plt.Line2D([0], [0], color='black', lw=4, alpha=0.3, label='Appearances'),
    plt.Line2D([0], [0], color='blue', lw=4, alpha=0.7, label='Hours played'),
]
ax.legend(custom_handles, labels + ['Appearances', 'Hours played']) # 범례 출력

plt.tight_layout() # 레이아웃 조정
plt.show() # 출력

# 그래프 2: 선수 경기 당 득점 수와 득점 당 평균 시간 (산점도)
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Goals per match', y='Minutes per goal', hue='Position', data=df, palette="Set1", s=100)

for i in range(df.shape[0]): # 선수 이름 추가
    plt.text(
        df['Goals per match'].iloc[i],
        df['Minutes per goal'].iloc[i] + 2,
        f"{df['Rank'].iloc[i]} {df['Name'].iloc[i]}",  # Rank와 이름을 함께 표시
        fontsize=9, ha='center', va='bottom'  # 텍스트 위치 조정
    )

plt.annotate('Increase in Efficiency',  # 텍스트 내용
    xy=(0.65, 170),  # 화살표 끝점
    rotation=-35,  # 텍스트 기울기
    va='baseline',  # 텍스트 수직 정렬
    ha='center',  # 텍스트 수평 정렬
    fontsize=12,  # 텍스트 크기
)

plt.annotate('',
             xytext = (0.55, 210),
             xy = (0.75, 150),
             arrowprops=dict(color='black', arrowstyle='->', lw=4)  # 화살표 스타일
)

plt.title("Scoring Efficiency")
plt.tight_layout()
plt.show()

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

X = df[['Appearances', 'Hours played', 'Minutes per goal', 'Goals per match']]  # 특성 변수
y = df['Goals']  # 타깃 변수

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) # 훈련/테스트 데이터 분리

model = LinearRegression() # 모델 생성 및 학습
model.fit(X_train, y_train)

y_hat = model.predict(X_test) # 예측

mse = mean_squared_error(y_test, y_hat) # 평가
mae = mean_absolute_error(y_test, y_hat)
r2 = r2_score(y_test, y_hat)  # R^2 계산

print(f"\nMSE: {mse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"R^2: {r2:.2f}")

plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_hat, color='blue', alpha=0.6, label='Predicted vs Actual')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--', label='Perfect Prediction')
plt.xlabel("Actual Goals")
plt.ylabel("Predicted Goals")
plt.title("Linear Regression: Predicted vs Actual Goals")
plt.legend()
plt.tight_layout()
plt.show()
