import spacy
import PyPDF2
import re
import json
from skill_recommender import recommend_courses
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_entities(text):
    doc = nlp(text)

    name = extract_name(doc)
    email = extract_email(text)
    phone = extract_phone(text)
    education = extract_education(text)
    skills = extract_skills(text)

    # Function to match skills with categories and recommend courses
    recommended_courses = recommend_courses(skills)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "skills": skills,
        "recommended_courses": recommended_courses
    }
    

def extract_name(doc):
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not Found"

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    match = re.search(r"\+?\d[\d\s().-]{8,}\d", text)
    return match.group(0) if match else "Not Found"

def extract_education(text):
    education_keywords = ['bachelor', 'master', 'b.sc', 'm.sc', 'b.tech', 'm.tech', 'phd', 'mba']
    return [word for word in education_keywords if word.lower() in text.lower()]

def extract_skills(text):
    with open("skills_db.json", "r") as f:
        skill_keywords = json.load(f)

    found_skills = []
    for skill in skill_keywords:
        if skill.lower() in text.lower():
            found_skills.append(skill)
    return list(set(found_skills))

