import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

# URL 설정
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
    # 선수 이름 추출
    player_name = row.find("td", {"class": "hauptlink"}).get_text(strip=True)
    
    # 포지션 추출 (두 번째 행의 두 번째 td에서)
    position = row.find_all("td")[1].find_all("tr")[1].find_all("td")[0].get_text(strip=True)
    
    # 득점 정보 (5번째 td에서)
    goals = row.find_all("td")[5].get_text(strip=True)
    
    # 출전 시간 (9번째 td에서)
    minutes_played = row.find_all("td")[11].get_text(strip=True)
    
    # 경기당 득점 (10번째 td에서)
    goals_per_match = row.find_all("td")[13].get_text(strip=True)
    
    # 데이터 리스트에 추가
    data.append({
        "Player Name": player_name,
        "Position": position,
        "Goals": goals,
        "Minutes Played": minutes_played,
        "Goals per Match": goals_per_match
    })

# pandas DataFrame으로 변환
df = pd.DataFrame(data)
sys.stdout.reconfigure(encoding='utf-8')
# 데이터 확인
print(df.head())
