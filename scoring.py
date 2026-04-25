# ==============================
# NLP SCORING MODULE (FINAL)
# ==============================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load model ONCE (important for Streamlit performance)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Reference NCR examples (champion patterns)
# -----------------------------
REFERENCE_NCRS = [
    "Oil leakage detected due to seal failure during turbine inspection",
    "Thermal anomaly caused by bearing overheating in generator section",
    "Gearbox vibration observed during maintenance due to misalignment",
    "Generator overheating detected during operation monitoring",
    "Blade damage identified during inspection after storm conditions"
]


# =============================
# COMPLETENESS SCORE (5W1H)
# =============================
def completeness_score(res):
    required_fields = ["What", "Where", "When", "Why", "Who", "How"]
    score = 0

    for k in required_fields:
        val = str(res.get(k, "")).strip().lower()
        if val and val != "not specified":
            score += 1

    return score  # range: 0–6


# =============================
# SEMANTIC SCORE (BERT-based)
# =============================
def semantic_score(text):
    text = str(text)

    # Encode input + reference NCRs
    text_vec = model.encode([text])
    ref_vec = model.encode(REFERENCE_NCRS)

    # Compute similarity
    similarity = cosine_similarity(text_vec, ref_vec)[0]

    max_sim = max(similarity)  # best match

    # Scale to 0–4 (to match your system design)
    return round(max_sim * 4, 2)


# =============================
# FINAL CLASSIFICATION
# =============================
def classify(score):
    if score >= 8:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"