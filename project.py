from bs4 import BeautifulSoup
import requests
#import re
import pandas as pd
import matplotlib.pyplot as plt

url = "https://www.kaggle.com/datasets/whisperingkahuna/la-liga-202324-players-and-team-insights"
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'lxml')
rows = soup.select('div > ul > li')

file_path = './archive/laliga2023_34/accurate_cross_team.csv' # 파일 경로
df1 = pd.read_csv(file_path)
df1 = df1.loc[:, ['Rank', 'Team', 'Accurate Crosses per Match', 'Cross Success (%)', 'Matches']] # 데이터셋에서 열 선택
df1 = df1.set_index(['Rank']) # Rank 열을 행 index 설정

def high_qual(x):
    return x['Accurate Crosses per Match'] >= 5.0

#df1 = df1.groupby(['Accurate Crosses per Match'])
df1 = df1[df1.apply(high_qual, axis=1)] # 필터링

df1.plot()
plt.show() # 그래프 그리기

print(df1)
