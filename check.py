import re

with open(r'b:\ASTRAgram-main\backend-java\src\main\resources\static\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# split by function definition
components = re.split(r'\nfunction\s+([A-Za-z0-9_]+)\s*\(', text)

for i in range(1, len(components), 2):
    name = components[i]
    body = components[i+1]
    
    div_open = len(re.findall(r'<div\b[^>]*>', body))
    div_close = len(re.findall(r'</div>', body))
    
    if div_open != div_close:
        print(f"{name} has {div_open} <div>s but {div_close} </div>s. (Delta: {div_open - div_close})")

