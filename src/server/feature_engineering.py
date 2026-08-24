import re

COMMON_SKILLS_LIST = [
    "python", "pytorch", "tensorflow", "kubernetes", "docker", "ray", "pinecone", "milvus", "qdrant",
    "react", "typescript", "javascript", "fastapi", "django", "flask", "postgresql", "redis", "elasticsearch",
    "mlflow", "kubeflow", "vllm", "tensorrt", "aws", "gcp", "azure", "ci/cd", "go", "rust", "c++", "java"
]

def parse_job_description(text: str) -> dict:
    """
    Parse a job description string to extract structured features.
    """
    text_lower = text.lower()
    
    # 1. Experience Years Required
    experience_match = re.search(r"(\d+)\s*\+?\s*(?:-\s*\d+\s*)?\s*(?:years?|yrs?)\b", text_lower)
    exp_required = 3  # default
    if experience_match:
        exp_required = int(experience_match.group(1))
    
    # 2. Extract Skills (simple scanning)
    required_skills = []
    preferred_skills = []
    
    # Try to scan sections
    pref_section = ""
    pref_split = re.split(r"(?:preferred|preferred\s+skills|nice\s+to\s+have|desirable):", text_lower)
    if len(pref_split) > 1:
        pref_section = pref_split[1]
        
    for skill in COMMON_SKILLS_LIST:
        if re.search(rf"\b{re.escape(skill)}\b", text_lower):
            # Check if it belongs to preferred section specifically
            if pref_section and re.search(rf"\b{re.escape(skill)}\b", pref_section):
                preferred_skills.append(skill)
            else:
                required_skills.append(skill)
                
    if not required_skills:
        # Fallback scan of whole text
        for skill in COMMON_SKILLS_LIST:
            if re.search(rf"\b{re.escape(skill)}\b", text_lower):
                required_skills.append(skill)
                
    # 3. Domain keywords (ml, ai, frontend, cloud, etc.)
    domain_keywords = []
    for keyword in ["llm", "rag", "ai", "ml", "nlp", "frontend", "backend", "cloud", "devops"]:
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            domain_keywords.append(keyword)
            
    return {
        "text": text,
        "requiredSkills": required_skills or ["python"],
        "preferredSkills": preferred_skills,
        "experienceYearsRequired": exp_required,
        "domainKeywords": domain_keywords
    }
