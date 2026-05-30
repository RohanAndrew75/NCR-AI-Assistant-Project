# ==============================
# NLP SCORING MODULE (FINAL HYBRID)
# ==============================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from bert_score import score as bert_score
import re

def clean_for_scoring(text):                                                                                                                            # Added foreign language phrase stripping
     # Remove content inside single quotes
    return re.sub(r"'[^']*'", "", text).strip()

# -----------------------------
# Load model ONCE (important)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Reference NCR examples
# -----------------------------
REFERENCE_NCRS = [                                                                                                                                      # Expanded REFERENCE_NCRS list
    "Oil leakage detected in main gearbox seal by service technician during scheduled quarterly maintenance at offshore platform",
    "Thermal anomaly identified in generator bearing section via temperature monitoring system during normal operation in high wind conditions",
    "Gearbox vibration exceeding threshold observed by engineer during routine inspection due to shaft misalignment after recent overhaul",
    "Generator overheating detected by SCADA monitoring during peak load operation, investigated by electrical maintenance team",
    "Leading edge blade erosion identified during annual drone inspection following storm season at coastal wind farm",
    "Loose bolts found in yaw system housing by maintenance crew during post-shutdown inspection due to suspected assembly error",
    "Hydraulic fluid leak discovered in pitch system by technician during weekly walkthrough at onshore wind farm",
    "Electrical fault in control cabinet caused automatic turbine shutdown, identified remotely via condition monitoring system",
    "Crack detected in cast iron nacelle frame during visual inspection following high vibration alarm triggered by CMS",
    "Rotor blade delamination found during scheduled inspection by composite repair specialist after lightning strike event",
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
def semantic_score(text):                                                               # Modified 'semantic_score' to 'clean_for_scoring' which includes foreign language phrase stripping
    text = clean_for_scoring(str(text))

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
