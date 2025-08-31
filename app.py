import streamlit as st
import joblib
import numpy as np

# Load models + vectorizer
log_model = joblib.load("model/logistic.pkl")
rf_model = joblib.load("model/randomforest.pkl")
gb_model = joblib.load("model/gradientboost.pkl")  # 🔥 Gradient Boosting
xgb_model = joblib.load("model/xgboost.pkl")        # ⚡ XGBoost
vectorizer = joblib.load("model/vectorizer.pkl")

# Load LabelEncoder for XGBoost
le = joblib.load("model/labelencoder.pkl") if joblib.os.path.exists("model/labelencoder.pkl") else None

st.title(" AI vs Human Code Detector ")
st.write("Paste Python code below and check **final result** based on all models (majority vote + confidence).")

# Text area input
code_input = st.text_area("Enter your code here:", height=400)

if st.button("Detect"):
    if code_input.strip():
        X = vectorizer.transform([code_input])

        results = []

        # Logistic Regression
        pred = log_model.predict(X)[0]
        prob = log_model.predict_proba(X).max()
        results.append(("Logistic Regression", pred, prob))

        # Random Forest
        pred = rf_model.predict(X)[0]
        prob = rf_model.predict_proba(X).max()
        results.append(("Random Forest", pred, prob))

        # Gradient Boosting
        pred = gb_model.predict(X)[0]
        prob = gb_model.predict_proba(X).max()
        results.append(("Gradient Boosting", pred, prob))

        # XGBoost
        y_pred = xgb_model.predict(X)
        if le:
            pred = le.inverse_transform(y_pred)[0]
        else:
            pred = "ai" if y_pred[0] == 0 else "human"
        prob = xgb_model.predict_proba(X).max()
        results.append(("XGBoost", pred, prob))

        # Show all model outputs
        for model_name, prediction, prob in results:
            if prediction == "ai":
                st.error(f"🔹 {model_name}: AI-generated (confidence: {prob:.2f})")
            else:
                st.success(f"🔹 {model_name}: Human-written (confidence: {prob:.2f})")

        # -------------------------
        # 🏆 Final Decision Logic
        # -------------------------
        ai_votes = [prob for _, pred, prob in results if pred == "ai"]
        human_votes = [prob for _, pred, prob in results if pred == "human"]

        if len(ai_votes) > len(human_votes):
            final_pred = "ai"
            final_conf = np.mean(ai_votes)
        elif len(human_votes) > len(ai_votes):
            final_pred = "human"
            final_conf = np.mean(human_votes)
        else:  # tie → choose higher avg confidence
            avg_ai = np.mean(ai_votes) if ai_votes else 0
            avg_human = np.mean(human_votes) if human_votes else 0
            if avg_ai >= avg_human:
                final_pred = "ai"
                final_conf = avg_ai
            else:
                final_pred = "human"
                final_conf = avg_human

        # Show final decision
        st.markdown("---")
        if final_pred == "ai":
            st.error(f" **Final Result: AI-generated** (confidence: {final_conf:.2f})")
        else:
            st.success(f" **Final Result: Human-written** (confidence: {final_conf:.2f})")

    else:
        st.warning(" Please paste some Python code!")
