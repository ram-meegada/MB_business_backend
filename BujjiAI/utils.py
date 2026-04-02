from openai import OpenAI
import json
from django.conf import settings
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def extract_skills(job_description):
    job_description = ''''''

    PROMPT = """
    Extract the following from the job description:

    1. Skills categorized into:
    - technical_skills
    - soft_skills
    - business_skills
    - domain_skills
    - operational_skills

    2. Experience required:
    - min_years
    - max_years (if not mentioned, keep null)

    Rules:
    - Return ONLY valid JSON
    - No explanation
    - Use lowercase for skills
    - If experience is unclear, make a reasonable estimate

    Job Description:
    \"\"\"
    {job_description}
    \"\"\"
    """
    prompt = PROMPT.format(job_description=job_description)

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a data extraction engine."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content

    try:
        print(content, "------------------")
        match = re.search(r"\[.*?\]", content)

        if match:
            skills = json.loads(match.group())
        else:
            skills = []
    except Exception as err:
        print(f"Error occurred while parsing JSON: {err}")
        skills = []

    return skills


# Example usage
job_description = """
We are looking for a Python developer with experience in Django, Docker, AWS and Postgres and sql.
"""
