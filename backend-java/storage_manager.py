import os
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
USER_ID = "vedan123"

def get_courses_dir():
    return os.path.join(_HERE, "users", USER_ID, "courses")

def get_course_dir(course_id):
    course_dir = os.path.join(get_courses_dir(), course_id)
    os.makedirs(course_dir, exist_ok=True)
    return course_dir

def save_metadata(course_id, metadata):
    course_dir = get_course_dir(course_id)
    with open(os.path.join(course_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

def load_metadata(course_id):
    path = os.path.join(get_course_dir(course_id), "metadata.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return None

def save_course(course_id, title, summary):
    course_dir = get_course_dir(course_id)
    content = f"# {title}\n\n## Course Summary\n{summary}\n"
    with open(os.path.join(course_dir, "course.md"), "w", encoding="utf-8") as f:
        f.write(content)

def load_course(course_id):
    path = os.path.join(get_course_dir(course_id), "course.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def save_episode(course_id, ep_id, title, summary, text):
    course_dir = get_course_dir(course_id)
    content = f"# {title}\n\n## Summary\n{summary}\n\n## Transcript\n{text}\n"
    with open(os.path.join(course_dir, f"episode_{ep_id}.md"), "w", encoding="utf-8") as f:
        f.write(content)

def load_episode(course_id, ep_id):
    path = os.path.join(get_course_dir(course_id), f"episode_{ep_id}.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def save_quiz(course_id, ep_id, quiz_json):
    course_dir = get_course_dir(course_id)
    # Save as JSON for programmatic loading
    with open(os.path.join(course_dir, f"episode_{ep_id}_quiz.json"), "w", encoding="utf-8") as f:
        json.dump(quiz_json, f, indent=2)
    
    # Save as Markdown for readable format
    md_content = f"# Quiz for Episode {ep_id}\n\n"
    questions = quiz_json.get("questions", [])
    
    # If it's a placeholder quiz (Ollama offline), or empty
    if not questions:
        md_content += "_No questions generated._\n"
    
    for i, q in enumerate(questions):
        md_content += f"## Q{i+1}: {q.get('question', '')}\n"
        
        q_type = q.get("type", "single_mcq")
        if q_type == "single_mcq" or q_type == "multiple_mcq":
            if "options" in q:
                for opt in q["options"]:
                    md_content += f"- {opt}\n"
            ans = q.get('answer', '')
            if isinstance(ans, list):
                ans = ", ".join(ans)
            md_content += f"\n**Answer:** {ans}\n\n"
        elif q_type == "match_following":
            md_content += "**Options to Match:**\n"
            for p in q.get("pairs", []):
                md_content += f"- {p.get('left')} -> {p.get('right')}\n"
            md_content += "\n"

    with open(os.path.join(course_dir, f"episode_{ep_id}_quiz.md"), "w", encoding="utf-8") as f:
        f.write(md_content)

def load_quiz(course_id, ep_id):
    path = os.path.join(get_course_dir(course_id), f"episode_{ep_id}_quiz.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return None
