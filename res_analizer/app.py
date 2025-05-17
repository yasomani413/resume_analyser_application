import streamlit as st
import spacy
import PyPDF2
import re
import json

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# --- Resume Extraction Functions ---

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

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

def recommend_courses(skills):
    recommended = []
    with open("courses_list.json", "r") as f:
        courses_data = json.load(f)

    for skill in skills:
        for category, courses_list in courses_data.items():
            for course in courses_list:
                if skill.lower() in course['title'].lower() or skill.lower() in category.lower():
                    course_with_category = course.copy()
                    course_with_category["category"] = category  # Add category info
                    recommended.append(course_with_category)
    return recommended

def extract_entities(text):
    doc = nlp(text)

    name = extract_name(doc)
    email = extract_email(text)
    phone = extract_phone(text)
    education = extract_education(text)
    skills = extract_skills(text)

    recommended_courses = recommend_courses(skills)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "skills": skills,
        "recommended_courses": recommended_courses
    }

# --- Streamlit App UI ---

st.set_page_config(page_title="Smart Resume Analyser", layout="wide")
st.title("📄 Smart Resume Analyser")

uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    st.subheader("📄 Extracted Text Preview")
    st.text(text[:1000] + "...")  # Show only first 1000 characters

    with st.spinner("Analyzing Resume..."):
        data = extract_entities(text)

    st.subheader("🔍 Resume Analysis")
    st.write("**Name:**", data.get("name", "Not Found"))
    st.write("**Email:**", data.get("email", "Not Found"))
    st.write("**Phone:**", data.get("phone", "Not Found"))
    st.write("**Education:**", ", ".join(data.get("education", [])))
    st.write("**Skills:**", ", ".join(data.get("skills", [])))

    if data.get("recommended_courses"):
        st.subheader("🎓 Recommended Courses")
        for course in data["recommended_courses"]:
            st.markdown(
                f"- **{course.get('title', 'No Title')}**  \n"
                f"_Category: {course.get('category', 'N/A')}_  \n"
                f"[Course Link]({course.get('url', '#')})  \n"
                f"Price: {course.get('price', 'N/A')}"
            )
    else:
        st.info("No course recommendations found based on the extracted skills.")
