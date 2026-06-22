import urllib.request
import json

try:
    req = urllib.request.Request("http://localhost:11434/api/tags")
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        models = [m['name'] for m in data.get('models', [])]
        print("Installed models:", models)
except Exception as e:
    print("Error:", e)
