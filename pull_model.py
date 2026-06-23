import urllib.request
import json
import sys

def pull_model(name):
    print(f"Pulling {name}...")
    req = urllib.request.Request("http://localhost:11434/api/pull",
                                 data=json.dumps({"name": name}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            # stream output
            for line in response:
                print(line.decode('utf-8').strip())
    except Exception as e:
        print("Error pulling:", e)

pull_model("qwen2.5:3b-instruct")
