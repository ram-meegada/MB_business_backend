from django.db import models
from pgvector.django import VectorField


class Company(models.Model):
    name = models.CharField(max_length=255)
    slugname = models.CharField(max_length=255, unique=True)
    company_url = models.URLField()
    logo_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class JobRawData(models.Model):
    raw_html = models.BinaryField()
    scraped_at = models.DateTimeField(auto_now_add=True)


class Job(models.Model):
    LINKEDIN = 'LinkedIn'

    SOURCE_CHOICES = [
        (LINKEDIN, 'LinkedIn'),
    ]

    job_id = models.BigIntegerField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.TextField()
    primary_tech = models.CharField(max_length=50, blank=True)
    role_category = models.CharField(max_length=50, blank=True)
    min_experience = models.IntegerField(null=True, blank=True)
    max_experience = models.IntegerField(null=True, blank=True)
    location = models.TextField(null=True)
    job_url = models.URLField(max_length=500)
    description = models.TextField(null=True)
    posted_at = models.DateTimeField(null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="linkedin")
    payload = models.JSONField()
    raw_data = models.ForeignKey(JobRawData, on_delete=models.SET_NULL, null=True, blank=True)
    llm_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class SkillManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('technical_skills', 'Technical Skills'),
        ('soft_skills', 'Soft Skills'),
        ('business_skills', 'Business Skills'),
        ('domain_skills', 'Domain Skills'),
        ('operational_skills', 'Operational Skills'),
        ('others', 'Others'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='others')
    is_approved = models.BooleanField(default=False)

    objects = SkillManager()
    allobjects = models.Manager()

    class Meta:
        unique_together = ("name", "category")


class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("job", "skill")


ALLOWED_PRIMARY_TECH = [
    "python", "java", "dotnet", "javascript", "typescript", "react", "angular", "nodejs", "php", "ruby", "golang",
    "rust", "kotlin", "swift", "flutter", "sql", "mongodb", "aws", "azure", "gcp", "cloud", "devops", "security", "networking",
    "database", "sap", "salesforce", "embedded", "hardware", "support", "any", "others"
]

ALLOWED_ROLE_CATEGORY = [
    "backend", "frontend", "fullstack", "mobile", "qa", "data", "science", "ai", "ml", "devops", "sre",
    "security", "soc", "network", "dba", "sysadmin", "support", "business", "product", "scrum", "architect", "embedded", "erp"
]

SKILLS_MAPPING = {
    "technical_skills": [
        "python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust", "kotlin", "swift", "php", "ruby", "scala", "matlab",
        "artificial intelligence", "machine learning", "deep learning", "natural language processing", "computer vision",
        "generative ai", "large language models", "neural networks", "reinforcement learning", "transfer learning", "prompt engineering",
        "data science", "data analysis", "data engineering", "data visualization", "statistics", "predictive modeling", "big data", "etl", "data mining",
        "pandas", "numpy", "scikit-learn", "devops", "cloud",
        "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis", "cassandra", "dynamodb", "database design", "query optimization",
        "html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot", "express.js",
        "rest api", "graphql", "websockets",
        "docker", "kubernetes", "ci/cd", "aws", "azure", "google cloud platform", "terraform", "ansible", "jenkins", "cloud architecture", "serverless",
        "react native", "flutter", "android", "ios",
        "unit testing", "integration testing", "test automation", "selenium", "pytest",
        "cybersecurity", "network security", "penetration testing", "ethical hacking", "encryption", "oauth", "jwt",
        "distributed systems", "microservices", "system design", "api design", "message queues", "kafka", "rabbitmq",
        "git", "github", "gitlab", "bitbucket"
    ],

    "soft_skills": [
        "communication", "leadership", "teamwork", "problem solving", "critical thinking", "time management",
        "adaptability", "creativity", "decision making", "conflict resolution", "emotional intelligence",
        "negotiation", "presentation skills", "collaboration", "work ethic"
    ],

    "business_skills": [
        "business strategy", "market research", "financial analysis", "budgeting", "forecasting",
        "stakeholder management", "product management", "business development", "sales",
        "marketing strategy", "customer relationship management", "pricing strategy", "revenue growth"
    ],

    "domain_skills": [
        "fintech", "healthcare", "e-commerce", "banking", "insurance", "logistics",
        "supply chain", "retail", "education technology", "real estate",
        "telecommunications", "manufacturing"
    ],

    "operational_skills": [
        "project management", "agile", "scrum", "kanban", "process improvement",
        "operations management", "risk management", "quality assurance",
        "six sigma", "lean methodology", "resource planning", "workflow optimization"
    ]
}
