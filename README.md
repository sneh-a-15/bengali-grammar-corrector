# Bengali Grammar Correction System

A simple **rule-based Bengali grammar correction tool** built using **Python**, **Streamlit**, and **Levenshtein Distance**.
It automatically fixes spelling and grammatical mistakes in Bengali sentences.

---

## ⚙️ Features

* 🧠 Rule-based + Edit-distance correction
* ✏️ Conservative and Aggressive modes
* 🚀 Fast, lightweight, and works offline
* 💻 Interactive Streamlit interface
* 📊 Displays model accuracy and edit distance

---

## 🧩 Installation

1. **Clone the project**

   ```bash
   git clone https://github.com/sneh-a-15/bengali-grammar-corrector.git
   cd bengali-grammar-corrector
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**

   ```bash
   streamlit run app.py
   ```

---

## 💻 Usage

1. Type or paste a Bengali sentence in the text box.
2. Select correction mode:

   * **Conservative** → Minimal, safer corrections
   * **Aggressive** → More character-level changes
3. Click **“Correct Sentence”** to see the corrected output.

---

## 🧮 Example

**Input:**

> তিনি একজন বীজ্ঞানী।

**Output:**

> তিনি একজন বিজ্ঞানী।

**Edit Distance:** 2

---

## 📁 Project Structure

```
📂 bengali-grammar-corrector/
 ├── app.py                 
 ├── model/
 │    └── improved_corrector.pkl
 ├── data/
 │    └── simple_50k_unique_1.csv
 ├── requirements.txt
 └── README.md
```

---

## ❤️ Credits

Built using **Python**, **Streamlit**, and **python-Levenshtein** for fast edit-distance correction.
