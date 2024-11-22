import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# 웹 크롤링 주소
url = "https://www.transfermarkt.com/premier-league/torschuetzenliste/wettbewerb/GB1/saison_id/2023/altersklasse/alle/detailpos//plus/1"

# User-Agent 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# HTTP 요청 및 HTML 파싱
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
else:
    print(f"Failed to fetch data: {response.status_code}")
    exit()

# 데이터 테이블 찾기
table_rows = soup.find_all("tr", {"class": ["odd", "even"]})

# 데이터 수집
data = []
for row in table_rows:
    rank = row.find("td", {"class": "zentriert"}).get_text(strip=True)
    name = row.find("td", {"class": "hauptlink"}).get_text(strip=True)
    position = row.find_all("td")[1].find_all("tr")[1].find_all("td")[0].get_text(strip=True)
    appearances = int(row.find_all("td")[8].get_text(strip=True))
    penalty_kicks = int(row.find_all("td")[10].get_text(strip=True))
    minutes_played = float(row.find_all("td")[11].get_text(strip=True).replace("'", ""))
    minutes_per_goal = int(row.find_all("td")[12].get_text(strip=True).replace("'", ""))
    goals_per_match = float(row.find_all("td")[13].get_text(strip=True))
    goals = int(row.find_all("td")[14].get_text(strip=True))
    
    data.append({
        "Rank": rank,
        "Name": name,
        "Position": position,
        "Appearances": appearances,
        "Penalty kicks": penalty_kicks,
        "Minutes Played": minutes_played,
        "Minutes per goal": minutes_per_goal,
        "Goals per Match": goals_per_match,
        "Goals": goals
    })

# DataFrame으로 변환
df = pd.DataFrame(data)
df.set_index("Rank", inplace=True)

# 목표 변수 (타깃) 및 특성 (입력 변수) 선택
X = df[["Appearances", "Penalty kicks", "Minutes Played", "Minutes per goal", "Goals per Match"]]  # 입력 변수
y = df["Goals"]  # 타깃 변수

# 데이터 분할: 훈련 세트(80%)와 테스트 세트(20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 초기화 및 학습
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# 예측
y_pred = model.predict(X_test)

# 평가
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error (MSE): {mse}")
print(f"R² Score: {r2}")

# 예측 결과 시각화
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--')
plt.xlabel('Actual Goals')
plt.ylabel('Predicted Goals')
plt.title('Actual vs Predicted Goals')
plt.show()
