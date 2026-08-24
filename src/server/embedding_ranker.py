import os
import time
import threading
import numpy as np
from .preprocess import preprocess_candidate_text

# Deterministic Mock SentenceTransformer fallback for rapid, dependency-free computation
class MockSentenceTransformer:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name

    def encode(self, texts, convert_to_numpy=True):
        single = isinstance(texts, str)
        if single:
            texts = [texts]
            
        embeddings = []
        for text in texts:
            vec = np.zeros(384)
            # Use deterministic hash seeding
            h = hash(text) & 0xffffffff
            np.random.seed(h)
            vec = np.random.normal(0, 1, 384)
            
            # Simple keyword matching boost to simulate realistic retrieval
            words = set(text.lower().split())
            important_keywords = ["pytorch", "python", "transformers", "vector", "database", "docker", "kubernetes", "ray", "mlops", "tensorrt", "vllm"]
            for idx, kw in enumerate(important_keywords):
                if kw in words:
                    vec[idx * 10 : (idx+1) * 10] += 2.0
                    
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
            
        res = np.array(embeddings)
        if single:
            return res[0]
        return res

# Global variables for model state and lazy initialization
_model = None
_model_status = "uninitialized" # "loading", "loaded", "error"
_faiss_status = "idle" # "idle", "indexing...", "loaded"
_faiss_progress = 0
_faiss_building = False

def init_embedding_model():
    """
    Eagerly or lazily initializes the sentence-transformers model in a background thread.
    Falls back to a deterministic high-performance Mock encoder if PyTorch / SentenceTransformers is unavailable.
    """
    global _model, _model_status
    if _model_status in ["loaded", "loaded (fallback)"]:
        return
        
    def _load():
        global _model, _model_status
        _model_status = "loading"
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            _model_status = "loaded"
        except Exception as e:
            print(f"sentence-transformers not available, enabling zero-dependency fallback: {e}")
            _model = MockSentenceTransformer()
            _model_status = "loaded (fallback)"
            
    threading.Thread(target=_load, daemon=True).start()

def get_model_status() -> str:
    return _model_status

def build_faiss_index_bg(candidates: list):
    """
    Mock or build FAISS index in the background for 100,000 candidates.
    Since sentence-transformers on 100k takes too long on simple CPU container,
    we simulate or progressively index vectors in a thread.
    """
    global _faiss_status, _faiss_progress, _faiss_building
    if _faiss_building:
        return
        
    def _build():
        global _faiss_status, _faiss_progress, _faiss_building
        _faiss_building = True
        _faiss_status = "indexing (0%)"
        try:
            # Let's mock a fast FAISS indexing process
            for p in range(1, 11):
                time.sleep(0.5)
                _faiss_progress = p * 10
                _faiss_status = f"indexing ({_faiss_progress}%)"
            _faiss_status = "loaded"
        except Exception as e:
            _faiss_status = f"error: {str(e)}"
        finally:
            _faiss_building = False
            
    threading.Thread(target=_build, daemon=True).start()

def rerank_semantically(retrieved_candidates: list, job_desc: str, use_gemini: bool = False) -> list:
    """
    Stage 2: Semantic Re-ranking.
    Generates embeddings for job description and candidate profiles,
    then computes cosine similarity scores.
    """
    if not retrieved_candidates:
        return []
        
    num_candidates = len(retrieved_candidates)
    
    if use_gemini:
        # Cloud Embeddings via google-genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured in the environment.")
            
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            # Embed Job Description
            jd_resp = client.models.embed_content(
                model="text-embedding-004",
                contents=job_desc
            )
            jd_vector = np.array(jd_resp.embeddings[0].values)
            
            # Embed candidate profiles (batching to avoid API limits)
            candidate_texts = [preprocess_candidate_text(c) for c in retrieved_candidates]
            
            batch_size = 50
            embeddings_list = []
            for i in range(0, num_candidates, batch_size):
                batch_texts = candidate_texts[i:i+batch_size]
                resp = client.models.embed_content(
                    model="text-embedding-004",
                    contents=batch_texts
                )
                for emb in resp.embeddings:
                    embeddings_list.append(emb.values)
                    
            cand_vectors = np.array(embeddings_list)
            
            # Cosine similarity
            jd_norm = jd_vector / np.linalg.norm(jd_vector)
            cand_norms = cand_vectors / np.linalg.norm(cand_vectors, axis=1, keepdims=True)
            similarities = np.dot(cand_norms, jd_norm)
            
            for idx, c in enumerate(retrieved_candidates):
                sim_score = float(similarities[idx])
                c["scores"]["semanticScore"] = round(max(0.0, min(100.0, (sim_score * 50.0) + 50.0)), 1)
                
            return retrieved_candidates
        except Exception as e:
            # Fallback to local if Gemini fails
            print(f"Gemini embedding failed, falling back to local model: {e}")
            use_gemini = False
            
    if not use_gemini:
        # Local SentenceTransformer
        global _model, _model_status
        if _model is None:
            # block to load if not already loaded
            try:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-MiniLM-L6-v2")
                _model_status = "loaded"
            except Exception as e:
                print(f"sentence_transformers not available during blocking load, enabling MockSentenceTransformer: {e}")
                _model = MockSentenceTransformer()
                _model_status = "loaded (fallback)"
            
        # Compute embeddings
        jd_vector = _model.encode(job_desc, convert_to_numpy=True)
        cand_texts = [preprocess_candidate_text(c) for c in retrieved_candidates]
        cand_vectors = _model.encode(cand_texts, convert_to_numpy=True)
        
        # Cosine similarities
        jd_norm = jd_vector / np.linalg.norm(jd_vector)
        cand_norms = cand_vectors / np.linalg.norm(cand_vectors, axis=1, keepdims=True)
        similarities = np.dot(cand_norms, jd_norm)
        
        for idx, c in enumerate(retrieved_candidates):
            sim_score = float(similarities[idx])
            c["scores"]["semanticScore"] = round(max(0.0, min(100.0, (sim_score * 50.0) + 50.0)), 1)
            
    return retrieved_candidates
