import pandas as pd
import json
import re
from collections import Counter

print("Loading LDJSON file...")
file_path = "jobs.ldjson"

# Read LDJSON file
data = []
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found!")
    exit(1)

print(f"Loaded {len(data)} job records")
df = pd.DataFrame(data)
print(f"DataFrame shape: {df.shape}")

print("\nExtracting relevant columns...")
# Create a clean dataframe with only the columns we need
df_clean = pd.DataFrame({
    'job_id': df['uniq_id'],
    'job_title': df['job_title'],
    'company_name': df['company_name'],
    'city': df['city'],
    'state': df['state'],
    'country': df['country'],
    'job_description': df['job_description'],
    'job_type': df['job_type'],
    'is_remote': df['is_remote'],
    'posting_date': df['post_date'],
    'job_link': df['url'],
    'category': df['category'],
    'company_description': df['company_description']
})

print("Cleaning data...")

# Handle missing values
df_clean['job_title'] = df_clean['job_title'].fillna('Unknown')
df_clean['company_name'] = df_clean['company_name'].fillna('Unknown')
df_clean['city'] = df_clean['city'].fillna('Unknown')
df_clean['state'] = df_clean['state'].fillna('Unknown')
df_clean['country'] = df_clean['country'].fillna('IN')
df_clean['job_description'] = df_clean['job_description'].fillna('')
df_clean['job_type'] = df_clean['job_type'].fillna('Not Specified')
df_clean['category'] = df_clean['category'].fillna('Other')

# Clean boolean column
df_clean['is_remote'] = df_clean['is_remote'].apply(lambda x: 1 if str(x).lower() in ['true', '1', 'yes'] else 0)

# Convert posting_date to datetime
df_clean['posting_date'] = pd.to_datetime(df_clean['posting_date'], errors='coerce')

# Remove duplicates
df_clean = df_clean.drop_duplicates(subset=['job_id'], keep='first')

# Remove rows with missing job_id
df_clean = df_clean.dropna(subset=['job_id'])

print(f"Data cleaned. Shape: {df_clean.shape}")

print("\nExtracting skills...")
TECH_SKILLS = [
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
    'go', 'rust', 'typescript', 'scala', 'r programming', 'matlab',
    'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis', 'elasticsearch',
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
    'spring', 'asp.net', 'fastapi', 'graphql', 'rest api',
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins',
    'git', 'linux', 'windows server', 'unix', 'bash', 'shell scripting',
    'power bi', 'tableau', 'excel', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
    'machine learning', 'deep learning', 'nlp', 'data science', 'data analytics',
    'agile', 'scrum', 'jira', 'confluence', 'salesforce', 'sap',
    'microservices', 'api', 'rest', 'soap', 'message queue', 'rabbitmq', 'kafka',
    'testing', 'junit', 'selenium', 'automation', 'ci/cd', 'devops'
]

def extract_skills(text):
    if not text or not isinstance(text, str):
        return []
    text_lower = text.lower()
    found_skills = []
    for skill in TECH_SKILLS:
        if skill in text_lower:
            found_skills.append(skill)
    return list(set(found_skills))

df_clean['extracted_skills'] = df_clean['job_description'].apply(extract_skills)

jobs_with_skills = df_clean['extracted_skills'].apply(len) > 0
print(f"Jobs with extracted skills: {jobs_with_skills.sum()} / {len(df_clean)}")

print("\nExporting cleaned data...")

# Export jobs
jobs_export = df_clean[['job_id', 'job_title', 'company_name', 'city', 'state', 
                         'country', 'job_description', 'job_type', 'is_remote', 
                         'posting_date', 'job_link', 'category', 'company_description']].copy()
jobs_export.to_csv('cleaned_jobs.csv', index=False, encoding='utf-8')
print("✓ Saved: cleaned_jobs.csv")

# Export skills
skills_list = []
for idx, row in df_clean.iterrows():
    for skill in row['extracted_skills']:
        skills_list.append({'job_id': row['job_id'], 'skill': skill})

skills_df = pd.DataFrame(skills_list)
if len(skills_df) > 0:
    skills_df.to_csv('extracted_skills.csv', index=False, encoding='utf-8')
    print(f"✓ Saved: extracted_skills.csv ({len(skills_df)} skill mentions)")

print("\n" + "="*50)
print("DATA SUMMARY")
print("="*50)
print(f"Total jobs: {len(df_clean)}")
print(f"Unique companies: {df_clean['company_name'].nunique()}")
print(f"Unique cities: {df_clean['city'].nunique()}")
print(f"Unique job titles: {df_clean['job_title'].nunique()}")
print(f"Remote jobs: {df_clean['is_remote'].sum()}")
print(f"On-site jobs: {(df_clean['is_remote'] == 0).sum()}")
print(f"Job types: {df_clean['job_type'].unique()[:5]}...")
print(f"Date range: {df_clean['posting_date'].min()} to {df_clean['posting_date'].max()}")

print(f"\nTop 10 skills mentioned:")
all_skills = []
for skills in df_clean['extracted_skills']:
    all_skills.extend(skills)
skill_counts = Counter(all_skills)
for skill, count in skill_counts.most_common(10):
    print(f"  {skill}: {count} jobs")

print("\n✓ Data cleaning complete!")
print("Ready for MySQL import.")