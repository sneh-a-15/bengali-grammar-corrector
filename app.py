import streamlit as st
import pickle
from collections import defaultdict
from Levenshtein import distance as fast_distance

# ============================================================
# Define Corrector Class (Lightweight version for inference)
# ============================================================
class ImprovedBengaliCorrector:
    def __init__(self):
        self.correction_dict = {}
        self.word_corrections = defaultdict(lambda: defaultdict(int))
        self.best_word_corrections = {}
        self.edit_patterns = []
        self.bigram_corrections = defaultdict(lambda: defaultdict(int))
        self.accuracy_cons = 0
        self.accuracy_aggr = 0

    def _apply_edits(self, text):
        corrected = text
        for typ, old, new in self.edit_patterns:
            if typ == "sub" and old in corrected:
                corrected = corrected.replace(old, new)
        return corrected

    def correct(self, text, aggressive=False):
        text = str(text).strip()
        if not text:
            return text

        # 1️⃣ Exact match
        if text in self.correction_dict:
            return self.correction_dict[text]

        # 2️⃣ Similar sentence
        best_match, best_distance = None, float("inf")
        text_len = len(text)
        for inc, cor in list(self.correction_dict.items())[:3000]:
            if abs(len(inc) - text_len) > 4:
                continue
            d = fast_distance(text, inc)
            if d <= 3 and d < best_distance:
                best_distance, best_match = d, cor
        if best_match and best_distance <= 2:
            return best_match

        # 3️⃣ Word-level correction
        words, new_words = text.split(), []
        for i, w in enumerate(words):
            corrected = w
            if w in self.best_word_corrections:
                corrected = self.best_word_corrections[w]
            new_words.append(corrected)

        candidate = " ".join(new_words)
        if fast_distance(text, candidate) <= len(text) * 0.3:
            return candidate

        # 4️⃣ Aggressive mode
        if aggressive:
            corrected = self._apply_edits(text)
            if corrected != text:
                return corrected

        return text


# ============================================================
# Load Model (with accuracy values if available)
# ============================================================
@st.cache_resource
def load_corrector(model_path="model/simple_corrector.pkl"):
    with open(model_path, "rb") as f:
        data = pickle.load(f)

    corrector = ImprovedBengaliCorrector()
    corrector.correction_dict = data.get("correction_dict", {})
    corrector.word_corrections = defaultdict(lambda: defaultdict(int), data.get("word_corrections", {}))
    corrector.best_word_corrections = data.get("best_word_corrections", {})
    corrector.edit_patterns = data.get("edit_patterns", [])
    corrector.accuracy_cons = data.get("accuracy_cons", 0)
    corrector.accuracy_aggr = data.get("accuracy_aggr", 0)
    return corrector


# ============================================================
# Streamlit UI
# ============================================================
st.set_page_config(page_title="Bengali Grammar Corrector", page_icon="", layout="centered")

st.markdown(
    """
    <h1 style='text-align: center; color: #1f77b4;'>Bengali Grammar Correction System</h1>
    <h4 style='text-align: center; color: grey;'>Rule-Based + Edit Distance Model</h4>
    """,
    unsafe_allow_html=True,
)

# Load model
with st.spinner("Loading trained model..."):
    corrector = load_corrector("model/simple_corrector.pkl")
st.success("✅ Model Loaded Successfully!")

# Input Section
st.subheader("📝 Enter Bengali text to correct:")
user_input = st.text_area("Paste or type your sentence here:", height=150, placeholder="উদাহরণ: তিনি একজন বীজ্ঞানী।")

# Mode selector
mode = st.radio("Correction Mode:", ["🛡️ Conservative (Safe)", "⚡ Aggressive (More Changes)"])
aggressive = mode.startswith("⚡")

# Correction Button
if st.button("🔍 Correct Sentence"):
    if not user_input.strip():
        st.warning("Please enter some text first.")
    else:
        corrected = corrector.correct(user_input, aggressive=aggressive)
        dist = fast_distance(user_input, corrected)

        if corrected == user_input:
            st.info("✅ No corrections needed! Your sentence looks perfect.")
        else:
            st.markdown("### 🎯 Corrected Output:")
            st.markdown(
                f"""
                <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px;'>
                <b>{corrected}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(f"🧮 Edit Distance: {dist}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: grey;'>
    Developed with ❤️ using <b>Streamlit</b> · Bengali Grammar Corrector
    </div>
    """,
    unsafe_allow_html=True,
)
