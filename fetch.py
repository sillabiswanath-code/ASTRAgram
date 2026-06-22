import urllib.request

try:
    response = urllib.request.urlopen('http://localhost:8080/app.js')
    content = response.read().decode('utf-8')
    lines = content.split('\n')
    
    # Check the end of App component
    app_end_idx = -1
    for i, line in enumerate(lines):
        if "function App()" in line:
            app_start = i
        if "// Render the App" in line:
            app_end_idx = i
            break
            
    if app_end_idx != -1:
        print("Last 20 lines of App component:")
        for i in range(app_end_idx - 20, app_end_idx):
            print(f"{i+1}: {lines[i]}")
    else:
        print("Could not find '// Render the App'")
        
except Exception as e:
    print("Error:", e)
