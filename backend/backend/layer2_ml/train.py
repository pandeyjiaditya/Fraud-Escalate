import pandas as pd
from layer2_ml.text_model import train_model

df = pd.read_csv("datasets/phishing_data.csv")

train_model(df["text"], df["label"])