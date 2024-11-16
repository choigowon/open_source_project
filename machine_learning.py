# 득점 수치 예측 (회귀 모델)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# 데이터 분리
X = df_cleaned[["Minutes Played", "Goals per Match", "Appearances", "Scoring Rate"]]
y = df_cleaned["Goals"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = LinearRegression()
model.fit(X_train, y_train)

# 예측 및 평가
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"득점 예측 - MSE: {mse}, R²: {r2}")

# 득점왕 여부 예측 (분류 모델)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# 득점왕 여부를 라벨링 (최고 득점자는 1, 나머지는 0)
df_cleaned["Top Scorer"] = (df_cleaned["Goals"] == df_cleaned["Goals"].max()).astype(int)

X = df_cleaned[["Minutes Played", "Goals per Match", "Appearances", "Scoring Rate"]]
y = df_cleaned["Top Scorer"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Random Forest 분류 모델 학습
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# 예측 및 평가
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"득점왕 예측 - Accuracy: {accuracy}, F1 Score: {f1}")
