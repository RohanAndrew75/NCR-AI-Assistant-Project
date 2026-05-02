import json
import re
import streamlit as st

from config import model
from few_shot_examples import CHAMPION_NCRS
from learning import load_champion_examples


# ---------------- SESSION STATE INIT (SAFE) ----------------
if "api_count" not in st.session_state:
    st.session_state.api_count = 0


# ---------------- JSON EXTRACTOR ----------------
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(" JSON parse error:", e)
    return None


# ---------------- SAFE API CALL ----------------
def safe_generate(prompt):
    try:
        #  Double safety (important for reruns)
        if "api_count" not in st.session_state:
            st.session_state.api_count = 0

        st.session_state.api_count += 1
        print(f" GEMINI CALL #{st.session_state.api_count}")

        response = model.generate_content(prompt)
        return response

    except Exception as e:
        return {"error": str(e)}


# ---------------- CLEAN 5W1H ----------------
def clean_5w1h(result):
    def clean(text):
        return text.strip() if isinstance(text, str) else "Not specified"

    for key in ["What", "Where", "When", "Why", "Who", "How"]:
        result[key] = clean(result.get(key, "Not specified"))

    # Fix incorrect "How"
    if result.get("How") and any(
        w in result["How"].lower() for w in ["inspection", "observed", "found"]
    ):
        result["How"] = "Not specified"

    # Fix verbose "What"
    if result.get("What") and len(result["What"].split()) > 12:
        result["What"] = result["What"].split(".")[0]

    # Weak "Who"
    if result.get("Who") and "technician" in result["Who"].lower():
        result["Who"] = "Not specified"

    return result


# ---------------- MAIN ANALYSIS FUNCTION ----------------
def analyze_ncr(context):

    #  LOAD DYNAMIC LEARNING EXAMPLES
    dynamic_examples = load_champion_examples()

    prompt = f"""
You are an expert in wind turbine NCR validation.

Use these high-quality examples:
{CHAMPION_NCRS}

Learn from past good NCRs:
{dynamic_examples}

Extract 5W1H strictly:
- No hallucination
- Missing → "Not specified"
- Keep answers SHORT

NCR:
{context}

Return JSON:
{{
 "What": "",
 "Where": "",
 "When": "",
 "Why": "",
 "Who": "",
 "How": "",
 "Improved_Description": ""
}}
"""

    response = safe_generate(prompt)

    # ---------------- ERROR HANDLING ----------------
    if isinstance(response, dict) and "error" in response:
        return {"Error": response["error"]}

    # ---------------- PARSE RESPONSE ----------------
    parsed = extract_json(response.text)

    if parsed:
        return clean_5w1h(parsed)
    else:
        return {
            "Error": "Parsing failed",
            "Raw": response.text
        }