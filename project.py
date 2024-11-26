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
        "Hours played": round(minutes_played * 1000 / 60, 1), # 시 단위로 변경
        "Minutes per goal" : minutes_per_goal,
        "Goals per match": goals_per_match,
        "Field goals": goals - penalty_kicks # 전체 득점에서 페널티 킥은 제외
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

# 그래프 1: 선수 출전 시간과 경기 수 (막대 그래프)
df['Name'] = df['Rank'].astype(str) + ' ' + df['Name']  # Rank와 Name 결합한 열 생성
df_sorted = df.sort_values(by='Hours played', ascending=False)  # Appearances 순으로 내림차순 정렬
fig, ax = plt.subplots(figsize=(10, 6))  # 그래프 크기 조정

hours_bar = sns.barplot( # Hours played (출전 시간) 막대 그래프
    data=df_sorted,
    y='Name',  # y축: 선수 이름
    x='Hours played',  # x축: 출전 시간
    hue='Position',  # 포지션별 색상 구분
    dodge=False,
    alpha=0.7,  # 투명도 설정
    ax=ax
)

appearances_bar = sns.barplot( # Appearances (출전 경기 수) 막대 그래프
    data=df_sorted,
    y='Name',
    x='Appearances',
    color='black',
    alpha=0.3,
    ax=ax
)

ax.set_title('Playing Time and Appearances', fontsize=14) # 축 및 레이블 설정
ax.set_xlabel('Value', fontsize=12)
ax.set_ylabel('Player Name', fontsize=12)

handles, labels = ax.get_legend_handles_labels() # 범례 표시
custom_handles = handles + [
    plt.Line2D([0], [0], color='black', lw=4, alpha=0.3, label='Appearances'),
    plt.Line2D([0], [0], color='blue', lw=4, alpha=0.7, label='Hours played'),
]
ax.legend(custom_handles, labels + ['Appearances', 'Hours played'], bbox_to_anchor=(1, 1), loc='upper left')

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
    xy=(0.65, 190),  # 화살표 끝점 (효율 증가 방향을 가리킴)
    rotation=-35,  # 텍스트 기울기
    va='baseline',  # 텍스트 수직 정렬
    ha='center',  # 텍스트 수평 정렬
    fontsize=12,  # 텍스트 크기
)

plt.annotate('',
             xytext = (0.55, 230),
             xy = (0.75, 170),
             arrowprops=dict(color='black', arrowstyle='->', lw=4)  # 화살표 스타일
)

plt.title("Scoring Efficiency")
plt.xlabel("Goals per match")
plt.ylabel("Minutes per Goal")
plt.legend(title='Position', bbox_to_anchor=(1, 1), loc='upper left')
plt.tight_layout()
plt.show()

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# 데이터 준비
X = df[['Hours played', 'Appearances', 'Minutes per goal', 'Goals per match', 'Position']] # 특성 변수
y = df['Field goals']  # 목표 변수

# 훈련 세트와 테스트 세트 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 데이터 전처리 파이프라인
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['Hours played', 'Appearances', 'Minutes per goal', 'Goals per match']),  # 수치형 변수 스케일링
        ('cat', OneHotEncoder(), ['Position'])  # 범주형 변수 인코딩
    ]
)

# 모델 파이프라인 (전처리 + 회귀 모델)
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression()) # 선형 회귀 모델
])

# 모델 훈련
model.fit(X_train, y_train)

# 예측
y_pred = model.predict(X_test)

# 모델 평가
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"\nMean Squared Error: {mse:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f}")
print(f"R^2: {r2:.2f}")

plt.figure(figsize=(10, 6))

# 실제 값과 예측 값 비교
plt.scatter(y_test, y_pred, color='blue', label='Predicted vs Actual', alpha=0.7)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Perfect Prediction')

plt.title('Actual vs Predicted Field Goals', fontsize=14)
plt.xlabel('Actual Field Goals', fontsize=12)
plt.ylabel('Predicted Field Goals', fontsize=12)
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()
