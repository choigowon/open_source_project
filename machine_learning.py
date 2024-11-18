from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

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
