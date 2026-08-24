import os

def generate_heuristic_explanation(candidate: dict, job_desc_parsed: dict) -> str:
    """
    Generate clean, scannable heuristic justification explaining candidate suitability
    based on experience gap and technical keywords.
    """
    name = candidate.get("name", "Candidate")
    skills = candidate.get("skills", [])
    required = job_desc_parsed.get("requiredSkills", [])
    
    # Intersect
    matched = list(set([s.lower() for s in skills]).intersection(set([r.lower() for r in required])))
    exp_years = candidate.get("experience_years", 0)
    exp_required = job_desc_parsed.get("experienceYearsRequired", 3)
    
    reasons = []
    if matched:
        reasons.append(f"strong alignment on technical stack including {', '.join(matched[:3])}")
    if exp_years >= exp_required:
        reasons.append(f"substantial industry tenure ({exp_years} years) exceeding requested requirements")
    else:
        reasons.append(f"growing industry exposure with {exp_years} years of professional experience")
        
    github_stars = candidate.get("behavioral_signals", {}).get("github_stars", 0)
    if github_stars > 50:
        reasons.append(f"prominent community contributions and active code repository eminence ({github_stars} stars)")
        
    return f"{name} presents a solid profile showing " + ", and ".join(reasons) + "."

def generate_gemini_explanation(candidate: dict, job_desc: str) -> str:
    """
    Use Google Gemini to generate high-fidelity, explainable AI reasoning
    comparing the candidate's career timeline and skills to the requested position.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API Key is not configured. Falling back to heuristic reasoning justification."
        
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        timeline_items = []
        for j in candidate.get('career_history', []):
            timeline_items.append(f"- {j.get('title')} at {j.get('company')}: {j.get('description')}")
        timeline_str = "\n".join(timeline_items)
        
        prompt = f"""
        Analyze the candidate's suitability for the following job description. Write a concise, 2-sentence professional evaluation.
        
        Job Description:
        {job_desc}
        
        Candidate Profile:
        Name: {candidate.get('name')}
        Headline: {candidate.get('headline')}
        Experience: {candidate.get('experience_years')} years
        Skills: {', '.join(candidate.get('skills', []))}
        Education: {candidate.get('education')}
        
        Career Timeline:
        {timeline_str}
        
        Respond with ONLY the 2-sentence professional evaluation.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip().replace('"', '')
    except Exception as e:
        return f"Could not generate Gemini explanation: {str(e)}"
