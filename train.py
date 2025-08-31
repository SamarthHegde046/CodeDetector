import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

# Paths
ai_folder = "data/python/ai"
human_folder = "data/python/human"
data = []

# Load AI code files
for filename in os.listdir(ai_folder):
    if filename.endswith(".py"):
        with open(os.path.join(ai_folder, filename), "r", encoding="utf-8", errors="ignore") as f:
            data.append({"code": f.read(), "label": "ai"})

# Load Human code files
for filename in os.listdir(human_folder):
    if filename.endswith(".py"):
        with open(os.path.join(human_folder, filename), "r", encoding="utf-8", errors="ignore") as f:
            data.append({"code": f.read(), "label": "human"})

# Convert to DataFrame
df = pd.DataFrame(data)

# Features: character-level ngrams work well for code
vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3,5))
X = vectorizer.fit_transform(df["code"])
y = df["label"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Logistic Regression ---
log_model = LogisticRegression(max_iter=2000)
log_model.fit(X_train, y_train)
print("\n📊 Logistic Regression Results:")
print(classification_report(y_test, log_model.predict(X_test)))

# --- Random Forest ---
rf_model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
print("\n🌲 Random Forest Results:")
print(classification_report(y_test, rf_model.predict(X_test)))

# --- Gradient Boosting ---
gb_model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, random_state=42)
gb_model.fit(X_train, y_train)
print("\n🔥 Gradient Boosting Results:")
print(classification_report(y_test, gb_model.predict(X_test)))

# Encode labels for XGBoost
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

# --- XGBoost ---
xgb_model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric="logloss"
)
# ✅ Use encoded labels here
xgb_model.fit(X_train, y_train_enc)
print("\n⚡ XGBoost Results:")
print(classification_report(y_test_enc, xgb_model.predict(X_test), target_names=le.classes_))

# Evaluate Logistic Regression
y_pred_log = log_model.predict(X_test)
print("\n📊 Logistic Regression Results:")
print(classification_report(y_test, y_pred_log))

# Evaluate Random Forest
y_pred_rf = rf_model.predict(X_test)
print("\n🌲 Random Forest Results:")
print(classification_report(y_test, y_pred_rf))

# Evaluate Gradient Boosting
y_pred_gb = gb_model.predict(X_test)
print("\n🔥 Gradient Boosting Evaluation:")
print(classification_report(y_test, y_pred_gb))

# Evaluate XGBoost correctly
y_pred_xgb = xgb_model.predict(X_test)
print("\n⚡ XGBoost Evaluation:")
print(classification_report(y_test_enc, y_pred_xgb, target_names=le.classes_))


# Save both models + vectorizer
os.makedirs("model", exist_ok=True)
joblib.dump(log_model, "model/logistic.pkl")
joblib.dump(rf_model, "model/randomforest.pkl")
joblib.dump(gb_model, "model/gradientboost.pkl")
joblib.dump(vectorizer, "model/vectorizer.pkl")
joblib.dump(xgb_model, "model/xgboost.pkl")

print("✅ Model and vectorizer saved in 'model/' folder")
