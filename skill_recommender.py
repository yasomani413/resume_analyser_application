import json

def recommend_courses(skills):
    recommended = []
    for skill in skills:
        for category, courses_list in courses_list.items():
            for course in courses_list:
                if skill.lower() in course['title'].lower() or skill.lower() in category.lower():
                    recommended.append(course)
    return recommended
