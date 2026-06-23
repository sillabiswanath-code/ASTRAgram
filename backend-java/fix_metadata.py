import os
import json

def fix():
    users_dir = os.path.join(os.path.dirname(__file__), "users")
    for user_id in os.listdir(users_dir):
        courses_dir = os.path.join(users_dir, user_id, "courses")
        if not os.path.exists(courses_dir): continue
        for course_id in os.listdir(courses_dir):
            metadata_path = os.path.join(courses_dir, course_id, "metadata.json")
            if not os.path.exists(metadata_path): continue
            
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "course_init_data" in data and "segments" in data["course_init_data"]:
                print(f"Fixing {user_id} - {course_id}")
                new_segments = []
                for s in data["course_init_data"]["segments"]:
                    seg = s.copy()
                    seg["status"] = "unlocked" if seg["id"] == 1 else "locked"
                    
                    quiz_path = os.path.join(courses_dir, course_id, f"episode_{seg['id']}_quiz.json")
                    if os.path.exists(quiz_path):
                        try:
                            with open(quiz_path, "r", encoding="utf-8") as f:
                                seg["quiz"] = json.load(f)
                        except Exception as e:
                            print(f"Failed to load quiz {quiz_path}: {e}")
                    new_segments.append(seg)
                
                data["segments"] = new_segments
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

if __name__ == "__main__":
    fix()
