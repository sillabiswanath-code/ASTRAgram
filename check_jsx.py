import re

with open(r'b:\ASTRAgram-main\backend-java\src\main\resources\static\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'\{/\*.*?\*/\}', '', text, flags=re.DOTALL)
tags = re.finditer(r'<(/?[a-zA-Z0-9_-]+)([^>]*?)>', text)
stack = []

for m in tags:
    full = m.group(0)
    tag = m.group(1)
    
    # Check if self-closing
    if full.strip().endswith('/>') or tag.lower() in ['br', 'input', 'img', 'iframe']:
        continue
        
    if tag.startswith('/'):
        expected = tag[1:]
        if not stack:
            print(f"Empty stack for {full} at char {m.start()}")
            import sys; sys.exit(1)
        top = stack.pop()
        if top[0] != expected:
            print(f"Mismatch! Found {full}, expected </{top[0]}>. Opened <{top[0]}> at char {top[1]}")
            # print context around the mismatch
            print(f"Context of open tag:\n{text[top[1]-50:top[1]+100]}\n")
            print(f"Context of close tag:\n{text[m.start()-50:m.start()+100]}")
            import sys; sys.exit(1)
    else:
        stack.append((tag, m.start()))

if stack:
    print("Unclosed:", [(t[0], t[1]) for t in stack])
else:
    print("Perfectly balanced!")
