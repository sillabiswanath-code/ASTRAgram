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
            "temperature": 0.1
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

def fix_components():
    prompt = """You are an expert React debugger. The following two components are causing issues because they ignore props like 'currentView', 'setCurrentView', and 'onCodeGraphClick'. Also they are very barebones.
Rewrite them to be fully functional, styled with classes like 'navbar', 'nav-brand', 'nav-links', 'btn-primary', 'hero-section', 'course-grid'. Ensure they accept the correct props.

Code:
// Navbar component
function Navbar() {
 return (
 <nav>
 <ul>
 <li><a href="#">Home</a></li>
 <li><a href="#">Courses</a></li>
 <li><a href="#">Blog</a></li>
 <li><a href="#">Contact</a></li>
 </ul>
 </nav>
 );
}

// Home component
function Home() {
 return (
 <div className="home-container">
 <section className="hero">
 <h1>Learning is key to your success</h1>
 </section>
 <section className="course-grid">
 {/* Course grid code goes here */}
 </section>
 </div>
 );
}

Return ONLY the corrected raw JS code. No markdown."""
    print("Asking OpenHermes to fix the components...")
    res = query_ollama(prompt)
    with open("b:/ASTRAgram-main/frontend-pure/fixed_components.js", "w", encoding="utf-8") as f:
        f.write(res.replace('```javascript', '').replace('```jsx', '').replace('```', ''))

if __name__ == "__main__":
    fix_components()
    print("Fix complete!")
