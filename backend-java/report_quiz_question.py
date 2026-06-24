import sys
import json
import re
import storage_manager
import ollama_agent

def extract_transcript(episode_md):
    if not episode_md:
        return ""
    parts = episode_md.split("## Transcript\n")
    if len(parts) > 1:
        return parts[1].strip()
    return ""

def main():
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
        
    user_id = sys.argv[1]
    course_id = sys.argv[2]
    segment_id = sys.argv[3]
    question_index = int(sys.argv[4])
    
    storage_manager.USER_ID = user_id
    
    quiz = storage_manager.load_quiz(course_id, segment_id)
    if not quiz or "questions" not in quiz:
        print(json.dumps({"error": "Quiz not found"}))
        sys.exit(1)
        
    questions = quiz.get("questions", [])
    if question_index < 0 or question_index >= len(questions):
        print(json.dumps({"error": "Invalid question index"}))
        sys.exit(1)
        
    # Remove the reported question
    questions.pop(question_index)
    
    # Try to regenerate a new question to replace it
    episode_md = storage_manager.load_episode(course_id, segment_id)
    transcript = extract_transcript(episode_md)
    
    if transcript:
        prompt = (
            f"Episode {segment_id} — Educational Content Transcript:\n"
            f"{transcript[:6000]}\n\n"
            f"TASK: Generate exactly 1 replacement quiz question.\n"
            f"Difficulty should be 'medium' or 'hard'.\n\n"
            f"CRITICAL RULES:\n"
            f"1. DO NOT print any intermediate steps, reasoning, or evaluations.\n"
            f"2. DO NOT output any preamble or conversational text.\n"
            f"3. Directly output the FINAL JSON array immediately.\n\n"
            f"Output ONLY the JSON array containing 1 question object. Nothing else."
        )
        res = ollama_agent.query_ollama(prompt, model=ollama_agent.QUIZ_MODEL, system_prompt=ollama_agent.QUIZ_SYSTEM_PROMPT, timeout=45)
        
        if "error" not in res:
            raw = res["response"].strip()
            
            try:
                new_questions = ollama_agent.extract_json_array(raw)
                
                if new_questions and isinstance(new_questions, list) and len(new_questions) > 0:
                    new_q = new_questions[0]
                    # basic validation
                    if "type" in new_q and "question" in new_q and "difficulty" in new_q:
                        # Insert the new question roughly where the old one was
                        insert_pos = min(question_index, len(questions))
                        questions.insert(insert_pos, new_q)
            except Exception as e:
                pass # If generation fails, we still deleted the bad one, which is fine.

    quiz["questions"] = questions
    storage_manager.save_quiz(course_id, segment_id, quiz)
    
    # Sync metadata.json so the dashboard doesn't load a zombie quiz!
    metadata = storage_manager.load_metadata(course_id)
    if metadata and "course_init_data" in metadata and "segments" in metadata["course_init_data"]:
        for seg in metadata["course_init_data"]["segments"]:
            if str(seg.get("id")) == str(segment_id):
                seg["quiz"] = quiz
                break
        storage_manager.save_metadata(course_id, metadata)
    
    print(json.dumps({"success": True, "message": "Question replaced/removed successfully", "quiz": quiz}))

if __name__ == "__main__":
    main()
