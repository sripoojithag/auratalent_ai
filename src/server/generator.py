import random

NAMES = ["Liam", "Olivia", "Noah", "Emma", "Oliver", "Ava", "Elijah", "Charlotte", "William", "Sophia", 
         "James", "Amelia", "Benjamin", "Isabella", "Lucas", "Mia", "Henry", "Evelyn", "Alexander", "Harper"]
SURNAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
            "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

HEADLINES_ML = [
    "Senior Machine Learning Engineer", "Staff AI Infrastructure Engineer", "MLOps Team Lead", 
    "Senior Data Scientist (Deep Learning)", "LLM & Retrieval Specialist", "AI Platform Architect"
]
HEADLINES_FE = [
    "Senior React Architect", "Frontend Engineer (TypeScript)", "Staff UI Engineer",
    "Lead React Native Developer", "Web Applications Architect", "Principal UX Engineer"
]
HEADLINES_BE = [
    "Lead Backend Engineer", "Senior Python Systems Engineer", "Cloud Infrastructure Architect",
    "Staff API Developer", "Distributed Systems Engineer", "Principal FastAPI Developer"
]

COMPANIES = ["Google", "Meta", "Amazon", "Apple", "Microsoft", "Netflix", "Stripe", "OpenAI", "Anthropic", "Scale AI", "Databricks", "Snowflake", "Cohere"]
UNIVERSITIES = ["Stanford University", "MIT", "UC Berkeley", "Carnegie Mellon University", "Harvard University", "Georgia Tech", "Caltech", "University of Washington"]

SKILLS_ML = ["Python", "PyTorch", "TensorFlow", "Kubernetes", "Docker", "Ray", "Pinecone", "Milvus", "Qdrant", "MLflow", "Kubeflow", "vLLM", "TensorRT", "AWS", "GCP"]
SKILLS_FE = ["React", "TypeScript", "JavaScript", "Vite", "ESBuild", "Tailwind CSS", "Zustand", "Redux", "HTML5", "CSS3", "Next.js", "Jest", "Web-Vitals"]
SKILLS_BE = ["Python", "FastAPI", "Django", "Flask", "PostgreSQL", "Redis", "Elasticsearch", "Docker", "Kubernetes", "AWS", "GCP", "API Design", "OAuth", "Asyncio", "Go"]

def generate_candidate_dataset(size: int = 100000) -> list:
    candidates = []
    
    for i in range(size):
        c_id = f"cand-{i:06d}"
        name = f"{random.choice(NAMES)} {random.choice(SURNAMES)}"
        
        domain = random.choices([0, 1, 2], weights=[0.4, 0.3, 0.3], k=1)[0]
        
        if domain == 0:
            headline = random.choice(HEADLINES_ML)
            all_skills = SKILLS_ML
            headline_keyword = "ML"
        elif domain == 1:
            headline = random.choice(HEADLINES_FE)
            all_skills = SKILLS_FE
            headline_keyword = "UI"
        else:
            headline = random.choice(HEADLINES_BE)
            all_skills = SKILLS_BE
            headline_keyword = "Backend"
            
        exp_years = random.randint(1, 15)
        education = f"{random.choice(['B.S.', 'M.S.', 'Ph.D.'])} in Computer Science, {random.choice(UNIVERSITIES)}"
        
        skills = list(set(random.choices(all_skills, k=random.randint(5, 8))))
        
        career_history = []
        num_jobs = random.randint(2, 3)
        for j in range(num_jobs):
            company = random.choice(COMPANIES)
            job_title = f"{'Senior ' if j == 0 and exp_years > 5 else ''}{headline.replace('Senior ', '').replace('Staff ', '').replace('Lead ', '')}"
            
            desc = f"Designed and optimized core {headline_keyword} systems. Collaborated with multi-functional teams to ship key features and scale services. Utilized {', '.join(skills[:3])} to deliver measurable product improvements."
            career_history.append({
                "title": job_title,
                "company": company,
                "description": desc
            })
            
        skill_score = round(random.uniform(50.0, 95.0), 1)
        career_score = round(min(100.0, 40.0 + (exp_years * 4.0) + random.uniform(0, 15)), 1)
        # Synthetic behavioral score used only for prototype/scalability testing.
         # In production, this would be calculated from real behavioral signals.
        behavioral_score = round(random.uniform(60.0, 98.0), 1)
        
        scores = {
            "semanticScore": 0.0,
            "skillScore": skill_score,
            "careerScore": career_score,
            "behavioralScore": behavioral_score,
            "finalScore": 0.0
        }
        # Behavioral signals are intentionally empty because no real
         # GitHub/recruiter data is currently integrated.

        behavioral_signals = {}
        
        candidates.append({
            "candidate_id": c_id,
            "name": name,
            "headline": headline,
            "experience_years": exp_years,
            "education": education,
            "skills": skills,
            "scores": scores,
            "behavioral_signals": behavioral_signals,
            "career_history": career_history
        })
        
    return candidates
