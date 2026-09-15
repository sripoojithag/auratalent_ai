import time
from .feature_engineering import parse_job_description
from .retriever import retrieve_candidates
from .embedding_ranker import rerank_semantically
from .reasoning import generate_heuristic_explanation

def run_ranking_pipeline(candidates: list, config: dict) -> dict:
    """
    Main orchestrator for the AuraTalent AI ranking pipeline.
    Executes Stage 1 retrieval, Stage 2 semantic reranking, Stage 3 hybrid scoring,
    and explanation generation.
    """
    start_time = time.time()
    
    # 1. Parse Job Description
    parsed_features = parse_job_description(config["jobDescriptionText"])
    
    # 2. Stage 1 Retrieval
    stage1_start = time.time()
    retrieved = retrieve_candidates(candidates, parsed_features, config.get("topKRetrieval", 2000))
    stage1_time = int((time.time() - stage1_start) * 1000)
    
    # 3. Stage 2 Semantic Reranking
    stage2_start = time.time()
    use_gemini = config.get("useGeminiEmbedding", False)
    sem_reranked = rerank_semantically(retrieved, config["jobDescriptionText"], use_gemini)
    stage2_time = int((time.time() - stage2_start) * 1000)
    
    # 4. Stage 3 Hybrid Ranking
    weights = config.get("weights", {
        "semantic": 0.50,
        "skills": 0.25,
        "career": 0.15
    })
    
    req_skills = set([s.lower() for s in parsed_features["requiredSkills"]])
    pref_skills = set([s.lower() for s in parsed_features["preferredSkills"]])
    
    for c in sem_reranked:
        c_skills = set([s.lower() for s in c["skills"]])
        
        # Calculate dynamic Technical Skill Match Score
        req_match = len(req_skills.intersection(c_skills)) / max(1, len(req_skills))
        pref_match = len(pref_skills.intersection(c_skills)) / max(1, len(pref_skills)) if pref_skills else 1.0
        
        # Combine required (80%) and preferred (20%) skill match
        skill_score = (req_match * 80.0) + (pref_match * 20.0)
        c["scores"]["skillScore"] = round(skill_score, 1)
        
        # Dynamic Career Growth Score (Experience tenure + progression speed)
        exp_years = c.get("experience_years", 0)
        exp_req = parsed_features["experienceYearsRequired"]
        exp_score = min(100.0, (exp_years / max(1, exp_req)) * 80.0)
        if exp_years >= exp_req:
            exp_score += 20.0  # Bonus for meeting requirements
        c["scores"]["careerScore"] = round(min(100.0, exp_score), 1)
        
        # Behavioral Score
# Behavioral signals are currently synthetic for prototype/testing.
# In production, this would be calculated from real candidate data.

        behavioral_signals = c.get("behavioral_signals", {})

        if behavioral_signals:
            github_commits = behavioral_signals.get("github_commits_last_year", 0)
            response_rate = behavioral_signals.get("recruiter_response_rate", 0.5)

            beh_score = (
                min(100.0, (github_commits / 150.0) * 40.0)
                + (response_rate * 60.0)
            )

            c["scores"]["behavioralScore"] = round(
                min(100.0, beh_score), 1
            )
        else:
            c["scores"]["behavioralScore"] = 0.0
        
        # Calculate Hybrid Final Score
        final_score = (
            weights.get("semantic", 0.50) * c["scores"]["semanticScore"] +
            weights.get("skills", 0.25) * c["scores"]["skillScore"] +
            weights.get("career", 0.15) * c["scores"]["careerScore"]         )
        c["scores"]["finalScore"] = round(final_score, 1)
        
        # Heuristic explanation
        c["reasoning"] = generate_heuristic_explanation(c, parsed_features)
        
    # Sort by final score
    sem_reranked.sort(key=lambda x: x["scores"]["finalScore"], reverse=True)
    
    # Apply Rank numbers to top 100
    top_candidates = []
    for idx, c in enumerate(sem_reranked[:100]):
        c_copy = dict(c)
        c_copy["rank"] = idx + 1
        top_candidates.append(c_copy)
        
    total_time = int((time.time() - start_time) * 1000)
    
    telemetry = {
        "totalCandidates": len(candidates),
        "stage1CandidatesCount": len(retrieved),
        "stage1TimeMs": stage1_time,
        "stage2TimeMs": stage2_time,
        "totalTimeMs": total_time,
        "modelUsed": "Google Cloud text-embedding-004" if use_gemini else "Local SentenceTransformers all-MiniLM-L6-v2",
        "weights": weights
    }
    
    return {
        "topCandidates": top_candidates,
        "parsedFeatures": parsed_features,
        "telemetry": telemetry
    }
