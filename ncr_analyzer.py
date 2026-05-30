import json
import re
import streamlit as st
import time

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
def safe_generate(prompt):                                                                             # Added retry logic for API rate limiting
    try:
        if "api_count" not in st.session_state:
            st.session_state.api_count = 0
        st.session_state.api_count += 1

        for attempt in range(3):
            response = model.generate_content(prompt)
            return response
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            if attempt < 2:
                wait = 15 * (attempt + 1)
                st.warning(f"Rate limit hit, retrying in {wait}s...")
                time.sleep(wait)
            else:
                return {"error": "Rate limit exceeded. Please wait a few minutes and try again."}
        return {"error": error_msg}

# ---------------- CLEAN 5W1H ----------------
def clean_5w1h(result):                                                                               # Removed over-aggressive clean_5w1h rules
    def clean(text):
        return text.strip() if isinstance(text, str) else "Not specified"

    for key in ["What", "Where", "When", "Why", "Who", "How"]:
        result[key] = clean(result.get(key, "Not specified"))

    # Fix verbose "What" only if extremely long
    if result.get("What") and len(result["What"].split()) > 20:                                       # "What" was truncated at 12 words, changed to 20
        result["What"] = result["What"].split(".")[0]

    return result


# ---------------- MAIN ANALYSIS FUNCTION ----------------
def analyze_ncr(context):

    #  LOAD DYNAMIC LEARNING EXAMPLES
    dynamic_examples = load_champion_examples()                                                       # Improved prompt to account for 'How' and 'Who' in {dynamic examples}

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
- For "How": describe HOW the issue was detected, diagnosed, or actioned (e.g. "detected via abnormal noise during rotation", "identified during visual inspection")
- For "Who": include any role mentioned (technician, maintenance crew, engineer, etc.)
- Translate any non-English phrases to English before extracting

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