import requests
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

# 웹 크롤링 URL 및 헤더 설정
url = "https://www.transfermarkt.com/premier-league/torschuetzenliste/wettbewerb/GB1/saison_id/2023/altersklasse/alle/detailpos//plus/1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# HTTP 요청 및 데이터 파싱
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
else:
    print(f"Failed to fetch data: {response.status_code}")
    exit()

# 테이블 행 데이터 추출
table_rows = soup.find_all("tr", {"class": ["odd", "even"]})
data = []

# 데이터 추출 및 리스트에 저장
for row in table_rows:
    try:
        rank = row.find("td", {"class": "zentriert"}).get_text(strip=True)
        player_name = row.find("td", {"class": "hauptlink"}).get_text(strip=True) # 이름
        position = row.find_all("td")[1].find_all("tr")[1].find_all("td")[0].get_text(strip=True) # 포지션
        appearances = int(row.find_all("td")[8].get_text(strip=True)) # 경기 수
        penalty_kicks = int(row.find_all("td")[10].get_text(strip=True)) # 페널티 킥 수
        minutes_played = float(row.find_all("td")[11].get_text(strip=True).replace("'", "")) # 출전 시간
        minutes_per_goal = int(row.find_all("td")[12].get_text(strip=True).replace("'", "")) # 득점 당 평균 시간
        goals_per_match = float(row.find_all("td")[13].get_text(strip=True)) # 경기 당 평균 득점
        goals = int(row.find_all("td")[14].get_text(strip=True)) # 득점 수
        
        data.append({
            "Rank": rank,
            "Player Name": player_name,
            "Position": position,
            "Appearances": appearances,
            "Goals": goals,
            "Penalty Kicks": penalty_kicks,
            "Minutes Played": minutes_played,
            "Minutes per Goal": minutes_per_goal,
            "Goals per Match": goals_per_match
        })
    except Exception as e:
        print(f"Error processing row: {e}")

# DataFrame 생성
df = pd.DataFrame(data)
df.set_index("Rank", inplace=True)

# 데이터 전처리: 목표는 'Goals' 예측
# 필요한 특성만 선택하여 X와 y 데이터 준비
X = df[["Appearances", "Minutes Played", "Goals per Match", "Penalty Kicks", "Minutes per Goal"]]
y = df["Goals"]

# 학습용 데이터와 테스트용 데이터로 나누기
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 선형 회귀 모델 학습
model = LinearRegression()
model.fit(X_train, y_train)

# 예측 수행
y_pred = model.predict(X_test)

# 평가 수치 계산
mae = mean_absolute_error(y_test, y_pred)  # 평균 절대 오차
r2 = r2_score(y_test, y_pred)  # 결정 계수 (R²)

# 평가 결과 출력
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"R² Score: {r2:.2f}")

# 회귀 계수와 절편 출력
print("Regression Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# 예측 결과 시각화
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, color='blue', alpha=0.6)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--')  # 대각선 (y=x) 추가
plt.title("Actual vs Predicted Goals")
plt.xlabel("Actual Goals")
plt.ylabel("Predicted Goals")
plt.show()
