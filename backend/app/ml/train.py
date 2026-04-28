import pandas as pd
import pickle
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("app/ml/data.csv")

FEATURES = ["distance", "weather", "traffic", "congestion"]
X = df[FEATURES]
y = df["delay"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBRegressor(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42
)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
print(f"Test MAE: {mae:.2f} hours")

pickle.dump(model, open("app/ml/model.pkl", "wb"))
print("Model saved -> app/ml/model.pkl")
