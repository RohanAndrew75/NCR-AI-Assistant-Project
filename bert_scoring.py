# ==============================
# NLP SCORING MODULE (FINAL HYBRID)
# ==============================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from bert_score import score as bert_score

# -----------------------------
# Load model ONCE (important)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Reference NCR examples
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

    return score  # 0–6


# =============================
# SEMANTIC SCORE (HYBRID)
# =============================
def semantic_score(text):
    text = str(text)

    # -------- EMBEDDING SIMILARITY --------
    text_vec = model.encode([text])
    ref_vec = model.encode(REFERENCE_NCRS)

    sim_scores = cosine_similarity(text_vec, ref_vec)[0]
    embedding_sim = max(sim_scores)  # 0–1

    # -------- BERT SCORE (F1) --------
    bert_scores = []

    for ref in REFERENCE_NCRS:
        _, _, F1 = bert_score(
            [text],
            [ref],
            lang="en",
            verbose=False
        )
        bert_scores.append(float(F1.mean()))

    bert_sim = max(bert_scores)  # best match

    # -------- COMBINE BOTH --------
    final_sim = (0.5 * embedding_sim) + (0.5 * bert_sim)

    # Scale to 0–4
    return round(final_sim * 4, 2)


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

def bert_semantic_score(text):
    text = str(text)

    bert_scores = []

    for ref in REFERENCE_NCRS:
        _, _, F1 = bert_score(
            [text],
            [ref],
            lang="en",
            verbose=False
        )
        bert_scores.append(float(F1.mean()))

    best_bert = max(bert_scores)

    return round(best_bert * 4, 2)