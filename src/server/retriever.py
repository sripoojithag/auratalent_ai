import time

def retrieve_candidates(candidates: list, parsed_features: dict, top_k: int = 2000) -> list:
    """
    Stage 1: Fast retrieval and filtering.
    Filters the 100,000 candidates to a top-K pool based on skills matching,
    experience requirements, and domain keyword presence.
    """
    required_skills = set([s.lower() for s in parsed_features.get("requiredSkills", [])])
    exp_required = parsed_features.get("experienceYearsRequired", 3)
    
    scored_candidates = []
    
    for c in candidates:
        c_skills = set([s.lower() for s in c.get("skills", [])])
        
        # Heuristic retrieval score calculation
        skill_intersect = len(required_skills.intersection(c_skills))
        
        exp_diff = c.get("experience_years", 0) - exp_required
        exp_penalty = max(0, -exp_diff) * 8.0 # penalty for missing required experience
        
        domain_match = 0
        headline_lower = c.get("headline", "").lower()
        for kw in parsed_features.get("domainKeywords", []):
            if kw.lower() in headline_lower:
                domain_match += 1
                
        retrieval_score = (skill_intersect * 25.0) + (c.get("experience_years", 0) * 2.0) + (domain_match * 15.0) - exp_penalty
        
        scored_candidates.append((retrieval_score, c))
        
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_candidates[:top_k]]
