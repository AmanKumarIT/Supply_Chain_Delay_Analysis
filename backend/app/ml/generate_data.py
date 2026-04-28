import pandas as pd
import numpy as np

np.random.seed(42)
n = 1000

df = pd.DataFrame({
    "distance":   np.random.uniform(200, 3000, n),
    "weather":    np.random.uniform(0, 1, n),
    "traffic":    np.random.uniform(0, 1, n),
    "congestion": np.random.uniform(0, 1, n),
})

# Delay is a linear combination of features with noise
df["delay"] = (
    df["distance"] * 0.005 +
    df["weather"]  * 20 +
    df["traffic"]  * 15 +
    df["congestion"] * 10 +
    np.random.normal(0, 2, n)
)

df.to_csv("app/ml/data.csv", index=False)
print(f"Generated {n} training samples -> app/ml/data.csv")
