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
        self.best_word_corrections = {}
        self.edit_patterns = []
        # ADDED: Smoothed bigram corrections for contextual lookup
        self.smoothed_bigram_corrections = {} 
        
        # NOTE: self.word_corrections and self.bigram_corrections (raw counts)
        # are not needed for inference, so they are kept empty or removed.
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

        # 2️⃣ Similar sentence (RELAXED THRESHOLD)
        best_match, best_distance = None, float("inf")
        text_len = len(text)
        for inc, cor in list(self.correction_dict.items())[:3000]:
            if abs(len(inc) - text_len) > 4:
                continue
            d = fast_distance(text, inc)
            
            # FIX 1a: Relaxed Distance Search (was d <= 3)
            if d <= 5 and d < best_distance:
                best_distance, best_match = d, cor
                
        # FIX 1b: Relaxed Distance Return (was best_distance <= 2)
        if best_match and best_distance <= 3:
            return best_match

        # 3️⃣ Word-level correction (WITH SMOOTHED BIGRAMS)
        words, new_words = text.split(), []
        changes = 0
        for i, w in enumerate(words):
            corrected = w
            
            # FIX 2: Check smoothed bigram corrections first
            if i > 0 and (words[i - 1], w) in self.smoothed_bigram_corrections:
                corrected = self.smoothed_bigram_corrections[(words[i - 1], w)]
            
            # Fall back to reliable single-word corrections (now count >= 1)
            elif w in self.best_word_corrections:
                corrected = self.best_word_corrections[w]
            
            if corrected != w:
                changes += 1
            new_words.append(corrected)

        candidate = " ".join(new_words)
        if changes > 0 and fast_distance(text, candidate) <= len(text) * 0.3:
            return candidate

        # 4️⃣ Aggressive mode
        if aggressive:
            corrected = self._apply_edits(text)
            if corrected != text:
                return corrected

        return text


# ============================================================
# Load Model (Updated to include smoothed_bigram_corrections)
# ============================================================
@st.cache_resource
def load_corrector(model_path="model/simple_corrector.pkl"):
    try:
        with open(model_path, "rb") as f:
            data = pickle.load(f)
    except FileNotFoundError:
        st.error(f"Error: Model file not found at {model_path}. Please run the training script first.")
        # Return a dummy corrector to prevent crash
        return ImprovedBengaliCorrector() 

    corrector = ImprovedBengaliCorrector()
    corrector.correction_dict = data.get("correction_dict", {})
    # Note: Loading raw word_corrections is not strictly needed for inference, but included for robustness
    corrector.best_word_corrections = data.get("best_word_corrections", {})
    corrector.edit_patterns = data.get("edit_patterns", [])
    
    # ADDED: Load smoothed bigram corrections
    corrector.smoothed_bigram_corrections = data.get("smoothed_bigram_corrections", {})
    
    # Load accuracy values for display if they exist
    corrector.accuracy_cons = data.get("accuracy_cons", 0)
    corrector.accuracy_aggr = data.get("accuracy_aggr", 0)
    return corrector


# ============================================================
# Streamlit UI
# ============================================================
st.set_page_config(page_title="Bengali Grammar Corrector", page_icon="🇧🇩", layout="centered")

st.markdown(
    """
    <h1 style='text-align: center; color: #1f77b4;'>Bengali Grammar Correction System</h1>
    <h4 style='text-align: center; color: grey;'>Rule-Based + Edit Distance Model (Max Coverage)</h4>
    """,
    unsafe_allow_html=True,
)

# Assume the model path used in training is correct
model_path = "model/simple_corrector.pkl" 
with st.spinner("Loading trained model..."):
    corrector = load_corrector(model_path)
st.success("✅ Model Loaded Successfully!")

# Display Accuracy metrics if available
if corrector.accuracy_cons > 0 or corrector.accuracy_aggr > 0:
    st.markdown("---")
    st.subheader("📊 Model Performance on Test Set:")
    col1, col2 = st.columns(2)
    col1.metric("Conservative Accuracy", f"{corrector.accuracy_cons:.2f}%")
    col2.metric("Aggressive Accuracy", f"{corrector.accuracy_aggr:.2f}%")
    st.markdown("---")

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