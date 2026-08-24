def preprocess_candidate_text(candidate: dict) -> str:
    """
    Format candidate's core profile, skills, and history into a rich text string
    optimized for semantic sentence embeddings.
    """
    headline = candidate.get("headline", "")
    skills = ", ".join(candidate.get("skills", []))
    education = candidate.get("education", "")
    
    # Format career history
    history_texts = []
    for job in candidate.get("career_history", []):
        history_texts.append(f"{job.get('title', '')} at {job.get('company', '')}: {job.get('description', '')}")
    history_str = " | ".join(history_texts)
    
    return f"Headline: {headline} | Skills: {skills} | Education: {education} | Experience: {history_str}"
