import streamlit as st
import pandas as pd
import csv
from datetime import datetime

from ncr_analyzer import analyze_ncr
from scoring import completeness_score, semantic_score, classify
from learning import load_champion_examples   # ⭐ NEW

# ---------------- LOAD DATA ----------------
def load_data():
    return pd.read_excel(
        r"data\wind_turbine_ncr_dataset_diverse_free_text_1000.xlsx"          # Fixed hardcoded dataset path
    )

df = load_data()

# ---------------- VALIDATION ----------------
def validate_input(text):
    if len(text.split()) < 8:
        return False, "NCR too short (minimum 8 words required)"
    return True, ""

# ---------------- FEEDBACK STORAGE ----------------
def save_feedback(user_input, result, feedback):
    file_name = "feedback_log.csv"

    comp = completeness_score(result)
    sem = semantic_score(user_input)
    final = round(comp + sem, 2)

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_ncr": user_input,

        "what": result.get("What"),
        "where": result.get("Where"),
        "when": result.get("When"),
        "why": result.get("Why"),
        "who": result.get("Who"),
        "how": result.get("How"),

        "improved_ncr": result.get("Improved_Description"),

        "completeness_score": comp,
        "semantic_score": round(sem, 2),
        "final_score": final,

        "feedback": feedback
    }

    try:
        with open(file_name, "r"):
            file_exists = True
    except:
        file_exists = False

    with open(file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


# ---------------- UI ----------------
st.title("🔧 NCR AI Assistant")
st.info("🧠 Continual Learning Enabled: AI adapts using past high-quality NCR feedback")

#  Show learning status (VERY IMPORTANT)
examples = load_champion_examples()
st.expander("🧠 Learned Examples").write(examples)

mode = st.radio("Choose Input Mode", ["Manual Input", "Dataset Sample"])

if mode == "Manual Input":
    user_input = st.text_area("Enter NCR Description")
else:
    idx = st.selectbox("Select NCR", df.index)
    row = df.loc[idx]
    user_input = row["NCR_Description"]
    st.write(row)


# ---------------- ANALYZE ----------------
if st.button("Analyze NCR"):

    if not user_input.strip():
        st.warning("Enter NCR first")
        st.stop()

    is_valid, msg = validate_input(user_input)
    if not is_valid:
        st.error(f"❌ {msg}")
        st.stop()

    with st.spinner("Analyzing NCR with AI..."):
        result = analyze_ncr(user_input)

    if "Error" in result:
        st.error("⚠️ AI failed or parsing issue")
        st.json(result)
        st.stop()

    #  STORE RESULT IN SESSION (IMPORTANT FIX)
    st.session_state["last_result"] = result
    st.session_state["last_input"] = user_input


# ---------------- DISPLAY RESULTS ----------------
if "last_result" in st.session_state:

    result = st.session_state["last_result"]
    user_input = st.session_state["last_input"]

    comp = completeness_score(result)
    sem = semantic_score(user_input)
    final = comp + sem
    quality = classify(final)

    if comp < 5:
        st.error("Missing critical 5W1H fields")
    elif final < 7:
        st.warning("NCR quality can be improved")
    else:
        st.success("NCR acceptable")

    st.subheader("📊 Evaluation Scores")                            # Improved Evaluation Scores UI
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Completeness", f"{comp:.2f}/6")
    e2.metric("Semantic", f"{sem:.2f}/4")
    e3.metric("Final Score", f"{final:.2f}/10")
    e4.metric("Quality", quality)
    st.progress(float(final) / 10)

    col1, col2 = st.columns(2)
    improved_text = result.get("Improved_Description", "")

    with col1:
        st.write("📄 Original NCR")
        st.info(user_input)

    with col2:
        st.write("✨ AI Improved NCR")
        st.success(improved_text)

    # -------- IMPROVEMENT COMPARISON --------
    if improved_text:
        st.subheader("📊 Improvement Comparison")   # Added Improvement Comparison panel between the original semantic score and the improved score

        imp_sem = round(semantic_score(improved_text), 2)
        delta = round(imp_sem - sem, 2)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Original Semantic", f"{sem}/4")
        c2.metric("Improved Semantic", f"{imp_sem}/4")
        c3.metric("Semantic Improvement", f"+{delta}" if delta >= 0 else str(delta))

    st.subheader("5W1H Extraction")
    for k in ["What", "Where", "When", "Why", "Who", "How"]:
        val = result.get(k, "Not specified")
        status = "✅" if val != "Not specified" else "❌"
        st.write(f"{status} **{k}:** {val}")

    # ---------------- MISSING FIELDS ----------------
    st.subheader("⚠️ Missing Fields")

    missing = []

    for field in ["What", "Where", "When", "Why", "Who", "How"]:
        val = result.get(field, "Not specified")
        if val == "Not specified":
            missing.append(field)

    if missing:
        for item in missing:
            st.write(f"❌ {item} is missing")
    else:
        st.success("No missing fields detected")

    # ---------------- FEEDBACK ----------------
    st.subheader(" Feedback System")

    feedback = st.radio(
        "Is this NCR analysis useful?",
        ["Good", "Average", "Poor"],
        horizontal=True
    )

    if st.button("Submit Feedback"):
        save_feedback(user_input, result, feedback)
        st.success("✔ Feedback saved successfully!")
        st.rerun()

    # ---------------- DEBUG ----------------
    with st.expander(" Debug Output"):
        st.json(result)