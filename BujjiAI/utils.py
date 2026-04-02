from openai import OpenAI
import json
from django.conf import settings
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def extract_skills(job_description):
    job_description = '''
About the role\nAt Flipkart, SDE-2 are engineers who create features based on product requirements. You’re expected to design and code in multiple tech components related to your functional area. You’re required to learn the best practices and design principles and patterns to make the code-base maintainable and extensible. You must also develop a deep understanding of non-functional requirements, such as reliability and availability, scale, horizontal scalability, etc. over time and make tech stack decisions accordingly.\nWe are looking for engineers who are well rounded - quality conscious, product thinkers, business\ncognizant and smart – not mere coders. Engineers get to significantly amplify their impact with the scale that Flipkart operates at.\nWhat you’ll do:\n● Design components by translating product requirements, break down project into tasks and\nprovide accurate estimates\n● Independently come up with different solutions, extensibile Low level design. Write modular,\nextensible, readable and performant code\n● Choose the right Data Structures, tools and tech stacks and be able to do High Level\nDesigning with guidance.\n● Build, develop, mentor and coach junior team members\n● Collaborate with teams by contributing to the shared vision and working closely with\ncross-functional stakeholders.\nWhat you’ll need:\n● B.Tech or M.Tech or equivalent with at least 3-year of experience\n● Build abstractions and contracts with separation of concerns for a larger scope.\n● Extensive programming experience in any one programming language like Java, Ruby, Clojure,\nScala,C or C++, SQL etc\n● Strong object-oriented programming skills.\n● Experience with multi-threading and concurrency programming\n● Ability to work with complex business flows and dealing with huge amounts of data.\n● Prior work experience in an agile environment or continuous integration and continuous delivery\n(CI or CD)\n● Experience of building robust and scalable web-application is good to have.
'''

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
