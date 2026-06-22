import urllib.request
import json
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt):
    payload = {
        "model": "openhermes",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"

def generate_styles():
    prompt = """You are an expert UI developer. Write ONLY the raw CSS code for a modern educational platform.
Include:
1. CSS variables for a blue primary color theme (--primary: #3b82f6).
2. A .navbar class for a top navigation bar.
3. A .hero-section class.
4. A .course-grid class for a grid layout.
5. .card, .btn-primary classes.
Return ONLY valid CSS code. Do not use markdown code blocks."""
    print("Generating styles.css with OpenHermes...")
    return query_ollama(prompt)

def generate_app_js():
    prompt = """You are an expert React developer. I have a React app that uses babel standalone.
Write the code for two React components: 'Navbar' and 'Home'. 
Navbar should have links: Home, Courses, Blog, Contact.
Home should have a hero section with title "Learning is key to your success" and a course grid.
Return ONLY the raw javascript code for these two functional components. Do not include markdown code blocks or imports."""
    print("Generating app.js components with OpenHermes...")
    return query_ollama(prompt)

if __name__ == "__main__":
    styles = generate_styles()
    app_js = generate_app_js()
    
    with open("b:/ASTRAgram-main/frontend-pure/openhermes_styles.css", "w", encoding="utf-8") as f:
        f.write(styles.replace('```css', '').replace('```', ''))
        
    with open("b:/ASTRAgram-main/frontend-pure/openhermes_components.js", "w", encoding="utf-8") as f:
        f.write(app_js.replace('```javascript', '').replace('```jsx', '').replace('```', ''))
        
    print("OpenHermes generation complete!")
