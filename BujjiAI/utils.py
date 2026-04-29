from openai import OpenAI
import json
from django.conf import settings
import re
import logging
from linkedIn_jobs.models import Skill, SKILLS_MAPPING
import numpy as np
from typing import Optional, Tuple
from django.db.models import QuerySet
from sympy import content
from BujjiAI.models import LLMUsage
import time
from linkedIn_jobs.models import Skill, JobSkill
from django.db import transaction


bujjiAI_logger = logging.getLogger('BujjiAI')

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def extract_skills_role_from_jd(job_description, job_id=None, request_type=LLMUsage.SKILLS_EXTRACTION):
    PROMPT = """
    Extract the following from the job description:

    ### Skill Categories
    * technical_skills
    * soft_skills
    * business_skills
    * domain_skills
    * operational_skills
    ---

    ### Instructions
    1. Extract only relevant skills from the job description.
    2. Normalize each skill to a **canonical name** from the predefined list whenever possible.
    3. If a skill appears in different forms (e.g., "ai", "ai tools", "ai technologies"), map it to the correct canonical form (e.g., "artificial intelligence").
    4. If no suitable match exists in the predefined list:
    * You MAY return a new skill.
    * Do NOT force-map it to an unrelated predefined skill.
    5. Prefer predefined skills over new ones whenever a reasonable match exists.
    6. Avoid duplicates:
    * Do not return both a predefined skill and a similar variation.
    * Return only the best normalized form.
    ---

    ### Normalization Rules
    * Use full, descriptive, and commonly accepted skill names
    (e.g., "artificial intelligence" instead of "ai")
    * Avoid abbreviations unless they are industry standard
    (e.g., "sql", "api")
    * Prefer canonical terms
    (e.g., "problem solving" instead of "problem-solving skills")
    * Do not return vague or incomplete terms
    (e.g., "analytical" → "analytical skills")
    * Remove duplicate or closely related variations
    * Keep the skill in respective category (e.g., "communication" in soft_skills, not technical_skills)
    ---

    ### Predefined Skill List

    #### technical_skills
    python, java, c, c++, c#, javascript, typescript, go, rust, kotlin, swift, php, ruby, scala, matlab,
    artificial intelligence, machine learning, deep learning, natural language processing, computer vision,
    generative ai, large language models, neural networks, reinforcement learning, transfer learning, prompt engineering,
    data science, data analysis, data engineering, data visualization, statistics, predictive modeling, big data, etl, data mining,
    pandas, numpy, scikit-learn, devops, cloud,
    sql, postgresql, mysql, sqlite, mongodb, redis, cassandra, dynamodb, database design, query optimization,
    html, css, react, angular, vue, node.js, django, flask, fastapi, spring boot, express.js,
    rest api, graphql, websockets,
    docker, kubernetes, ci/cd, aws, azure, google cloud platform, terraform, ansible, jenkins, cloud architecture, serverless,
    react native, flutter, android, ios,
    unit testing, integration testing, test automation, selenium, pytest,
    cybersecurity, network security, penetration testing, ethical hacking, encryption, oauth, jwt,
    distributed systems, microservices, system design, api design, message queues, kafka, rabbitmq,
    git, github, gitlab, bitbucket
    ---

    #### soft_skills
    communication, leadership, teamwork, problem solving, critical thinking, time management,
    adaptability, creativity, decision making, conflict resolution, emotional intelligence,
    negotiation, presentation skills, collaboration, work ethic
    ---

    #### business_skills
    business strategy, market research, financial analysis, budgeting, forecasting,
    stakeholder management, product management, business development, sales,
    marketing strategy, customer relationship management, pricing strategy, revenue growth
    ---

    #### domain_skills
    fintech, healthcare, e-commerce, banking, insurance, logistics,
    supply chain, retail, education technology, real estate,
    telecommunications, manufacturing
    ---

    #### operational_skills
    project management, agile, scrum, kanban, process improvement,
    operations management, risk management, quality assurance,
    six sigma, lean methodology, resource planning, workflow optimization
    ---

    2. Experience required:
    - min_years
    - max_years (if not mentioned, keep null)

    3. Normalization — extract TWO fields:
    A) primary_tech:
    - The PRIMARY technology or domain of the job based on what the company is expecting in the context.
    - Single word only.
    - Choose from:
        python, java, dotnet, javascript, typescript, react, angular, nodejs, php, ruby, golang,
        rust, kotlin, swift, flutter, sql, mongodb, aws, azure, gcp, cloud, devops, security, networking,
        database, sap, salesforce, embedded, hardware, support, any, others
    - Rules:
        * Pick the technology that is REQUIRED, not just "good to have"
        * If the job is infrastructure, deployment, or platform-focused:
          choose from "cloud", "devops", "security", "networking", "database" as primary_tech
        * If a specific platform is dominant (e.g., AWS), prefer that instead of generic terms
        * If the job accepts ANY programming language or is stack agnostic → return "any"
        * If the job role is not about IT sector → return "others"
    - Return only ONE word.

    B) role_category:
    - The FUNCTIONAL area the person works in.
    - Single word only.
    - Choose from:
        backend, frontend, fullstack, mobile, qa, data, science, ai, ml, devops, sre,
        security, soc, network, dba, sysadmin, support, business, product, scrum, architect, embedded, erp
    - Rules:
        * Based on RESPONSIBILITIES, not the job title
        * If mentioned GenAI/RAG/prompts → "ai"
        * "tester" or "automation tester" → always "qa"
        * "automation engineer" without QA signals → "devops"
        * Neural networks/LLMs/deep learning → "ml"
        * ETL/pipeline work → "data"
        * Research/modelling/algorithms → "science"
        * SOC/threat/incident response → "soc"
        * Security audits/pentesting → "security"
        * Intern roles still get functional category, captured in seniority
    - Return only ONE word.

    Examples:
    "Python Automation Tester"      → primary_tech: "python",      role_category: "qa"
    "Python Automation Engineer"    → primary_tech: "python",      role_category: "devops"
    "Data Engineer - Spark/Airflow" → primary_tech: "python",      role_category: "data"
    "Java Microservices Developer"  → primary_tech: "java",        role_category: "backend"
    "React Frontend Engineer"       → primary_tech: "react",       role_category: "frontend"
    "AWS Cloud Architect"           → primary_tech: "aws",         role_category: "architect"
    "SOC Analyst L2"                → primary_tech: "security",    role_category: "soc"
    "Salesforce Admin"              → primary_tech: "salesforce",  role_category: "erp"
    "Data Science Intern"           → primary_tech: "python",      role_category: "science"
    "Android Developer"             → primary_tech: "kotlin",      role_category: "mobile"
    "Power BI Analyst"              → primary_tech: "data",        role_category: "business"
    "ML Engineer - PyTorch"         → primary_tech: "python",      role_category: "ml"
    "Network Engineer - Cisco"      → primary_tech: "networking",  role_category: "network"
    "DBA - Oracle/PostgreSQL"       → primary_tech: "database",    role_category: "dba"
    "IT Helpdesk Support"           → primary_tech: "support",     role_category: "support"

    Output JSON structure (STRICT):
    {{
    "skills": {{
        "technical_skills": [],
        "soft_skills": [],
        "business_skills": [],
        "domain_skills": [],
        "operational_skills": []
    }},
    "experience": {{
        "min_years": number | null,
        "max_years": number | null
    }},
    "primary_tech": "string",
    "role_category": "string"
    }}

    Rules:
    - Return ONLY valid JSON
    - No explanation
    - No markdown code fences (do not use ```json or ```)
    - No preamble or extra text before or after the JSON
    - Use lowercase for skills
    - If experience is unclear, make a reasonable estimate

    Job Description:
    \"\"\"
    {job_description}
    \"\"\"
    """
    skills = []

    try:
        prompt = PROMPT.format(job_description=job_description)
        content = call_openai(prompt, system_role="You are a helpful assistant for parsing job descriptions.", request_type=request_type)
        skills = json.loads(content)
    except json.JSONDecodeError:
        print("JSON decoding error")
        bujjiAI_logger.error(f"JSON decoding error for job ID {job_id}. Response content: {content}")
    except Exception as err:
        print(err, 'error')
        bujjiAI_logger.exception(f"Error occurred while parsing JSON for job ID {job_id}: {err}")

    return skills


def call_openai(prompt, system_role, request_type):
    start = time.time()

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ]
    )

    track_llm_usage(response, request_type, start)
    content = response.choices[0].message.content
    return content


def track_llm_usage(response, request_type, start_time, **kwargs):
    try:
        usage = response.usage
        model = response.model

        LLMUsage.objects.create(
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=getattr(usage.prompt_tokens_details, 'cached_tokens', 0),
            latency_ms=int((time.time() - start_time) * 1000),
            request_type=request_type,
            cost=calculate_llm_request_cost(model, usage.prompt_tokens, usage.completion_tokens, getattr(usage.prompt_tokens_details, 'cached_tokens', 0))
        )

        return response

    except Exception as e:
        LLMUsage.objects.create(
            model=kwargs.get("model"),
            is_success=False,
            error_message=str(e),
            latency_ms=int((time.time() - start_time) * 1000),
            cost=0.0,
        )
        raise


def calculate_llm_request_cost(model, prompt_tokens, completion_tokens, cached_tokens=0):
    pricing = settings.CHARGES.get(model, {})
    non_cached_tokens = prompt_tokens - cached_tokens

    cost = (
        (non_cached_tokens/1_000_000) * pricing.get('input_cost', 0) +
        (cached_tokens/1_000_000) * pricing.get('cached_input', 0) +
        (completion_tokens/1_000_000) * pricing.get('output_cost', 0)
    )

    return cost


def generate_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",  # 1536 dimensions
        input=text
    )
    return response.data[0].embedding

def generate_all_embeddings():
    skills = Skill.objects.filter(embedding__isnull=True)

    for skill in skills:
        embedding = generate_embedding(skill.name)
        skill.embedding = embedding
        skill.save(update_fields=["embedding"])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def get_all_skill_embeddings(category: Optional[str] = None) -> list:
    qs: QuerySet = Skill.objects.exclude(embedding__isnull=True)

    if category:
        qs = qs.filter(category=category)

    return [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "embedding": np.array(s.embedding, dtype=np.float32),
        }
        for s in qs
    ]

def find_best_skill(
    input_text: str,
    category: Optional[str] = None,
    threshold: float = 0.85,
) -> Tuple[Optional[str], float]:
    """
    Returns:
        (best_skill_name, similarity_score)
    """

    # Step 1: generate embedding
    input_vec = np.array(generate_embedding(input_text), dtype=np.float32)

    # Step 2: load skills
    skills = get_all_skill_embeddings(category)

    if not skills:
        return None, 0.0

    # Step 3: compute similarity
    best_match = None
    best_score = -1.0

    for skill in skills:
        score = cosine_similarity(input_vec, skill["embedding"])

        if score > best_score:
            best_score = score
            best_match = skill["name"]

    # Step 4: apply threshold
    if best_score >= threshold:
        return best_match, best_score

    return None, best_score


class LLMExtractionManager:
    def __init__(self, jobs_qs):
        self.jobs_qs = jobs_qs  # Job.objects.filter(llm_processed=False, description__isnull=False)[:50]

    def start(self):
        try:
            with transaction.atomic():
                # pk_list = [21567, 20913, 20561, 18747, 17393, 17184, 16673, 22375, 22332]
                # pk_list = [16673]
                # jobs = Job.objects.filter(pk__in=pk_list)

                for job in self.jobs_qs:
                    bujjiAI_logger.info(f"Processing job ID {job.pk} - {job.title}")
                    result = extract_skills_role_from_jd(job.description, job_id=job.pk)
                    if not result:
                        bujjiAI_logger.info(f"No skills extracted for job ID {job.pk}")
                        continue
                    
                    bujjiAI_logger.info(f"Extracted data for job ID {job.pk}: {result}")
                    skills_data = result.get("skills", {})
                    primary_tech = result.get("primary_tech", "")
                    role_category = result.get("role_category", "")
                    min_years_exp = result.get("experience", {}).get("min_years")
                    max_years_exp = result.get("experience", {}).get("max_years")

                    if not skills_data or not primary_tech or not role_category:
                        bujjiAI_logger.info(f"Insufficient data for job ID {job.pk}")
                        continue

                    job.min_experience = min_years_exp if min_years_exp is not None else None
                    job.max_experience = max_years_exp if max_years_exp is not None else None
                    job.primary_tech = primary_tech
                    job.role_category = role_category
                    job.llm_processed = True
                    job.save()

                    for category, skills in skills_data.items():
                        for skill_name in skills:
                            skill_obj, _ = Skill.allobjects.get_or_create(name=skill_name, category=category)
                            JobSkill.objects.get_or_create(job=job, skill=skill_obj)

                    bujjiAI_logger.info(f'processed job: {job.pk} - {job.title}')
        except Exception as e:
            bujjiAI_logger.error(f"Error processing jobs: {str(e)}")
