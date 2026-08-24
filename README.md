# AuraTalent AI 🤖

An AI-powered **candidate matching and ranking system** that helps recruiters identify the most relevant candidates for a given job description.

## 🚀 Features

* Semantic matching between job descriptions and candidate profiles
* Candidate ranking using a **hybrid scoring approach**
* Technical skill and experience matching
* Behavioral signals such as GitHub activity
* AI-powered candidate explanations using **Gemini**
* Configurable ranking weights
* Candidate results export to CSV
* Interactive recruitment dashboard

## 🧠 How It Works

```text
Job Description
       ↓
Feature Extraction
       ↓
Candidate Retrieval
       ↓
Semantic Similarity
       ↓
Skill + Experience + Behavioral Scoring
       ↓
Final Candidate Ranking
       ↓
AI-Generated Explanation
```

The final score combines:

* **Semantic similarity**
* **Technical skills**
* **Career experience**
* **Behavioral signals**

This allows the system to rank candidates based on multiple factors rather than relying only on keyword matching.

## 🛠️ Tech Stack

**Frontend**

* React
* TypeScript
* Vite
* Tailwind CSS

**Backend**

* Python
* FastAPI
* Streamlit

**AI / ML**

* Sentence Transformers
* `all-MiniLM-L6-v2`
* Google Gemini
* Cosine Similarity

**Data**

* Pandas
* NumPy

## 📂 Project Structure

```text
src/
├── server/
│   ├── embedding_ranker.py
│   ├── feature_engineering.py
│   ├── pipeline.py
│   ├── retriever.py
│   └── reasoning.py
│
├── App.tsx
└── types.ts

server.py
streamlit_app.py
requirements.txt
```

## ⚙️ Setup

### Clone the repository

```bash
git clone https://github.com/sripoojithag/auratalent_ai.git
cd auratalent_ai
```

### Install dependencies

```bash
npm install
pip install -r requirements.txt
```

### Run

```bash
npm start
```

For the Streamlit interface:

```bash
streamlit run streamlit_app.py
```

## 🔮 Future Improvements

* Real resume/PDF parsing
* Production vector database integration
* Recruiter feedback-based ranking
* Candidate comparison
* Bias and fairness evaluation
* Docker deployment



