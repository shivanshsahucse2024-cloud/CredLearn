import google.generativeai as genai
import os
import json
import random

import sys

# Configure Gemini
# We configure it lazily inside the function to ensure env vars are loaded

from dotenv import load_dotenv

# Force load env vars
load_dotenv()

def generate_quiz_questions(skill_name):
    """
    Generates 10 short-answer/one-liner questions for a given skill using Gemini 2.5 Flash.
    Returns a list of dictionaries: [{'id': 1, 'question': '...'}, ...]
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        error_msg = "GEMINI_API_KEY not found in .env file. Please check your configuration."
        print(f"DEBUG: {error_msg}", file=sys.stderr)
        raise ValueError(error_msg)
        
    genai.configure(api_key=api_key)

    try:
        print(f"DEBUG: Generating quiz for skill: {skill_name}", file=sys.stderr)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Analyze the input text: "{skill_name}".
        
        First, determine if this is a valid, verifiable human skill (it can be technical, artistic, soft skill, trade, language, etc.).
        
        If it is NOT a valid skill (e.g., gibberish, random numbers, offensive, or too vague to test), output strictly this JSON:
        {{ "error": "The input '{skill_name}' does not appear to be a verifiable skill." }}
        
        If it IS a valid skill, generate 10 questions to verify competence in this specific domain.
        The questions should be:
        1. Relevant to the specific nature of the skill.
        2. Short answer type (one-liners).
        3. Challenging enough to verify basic to intermediate competence.
        
        Output strictly in JSON format with a 'questions' key:
        {{
            "questions": [
                {{"id": 1, "question": "Question text here..."}},
                ...
            ]
        }}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        print(f"DEBUG: Gemini Response Text: {response.text}", file=sys.stderr)
        data = json.loads(response.text)
        
        if 'error' in data:
            raise ValueError(data['error'])
            
        return data.get('questions', [])
    except Exception as e:
        error_msg = str(e)
        if "Gemini API Error" not in error_msg: 
             # Keep clean user facing errors if we raised them
             pass
        else:
             error_msg = f"Gemini API Error: {str(e)}"
             
        print(f"DEBUG: {error_msg}", file=sys.stderr)
        raise ValueError(error_msg)


def grade_quiz_answers(skill_name, questions, user_answers):
    """
    Grades the user's answers using Gemini.
    questions: list of dicts [{'id': 1, 'question': '...'}]
    user_answers: dict { '1': 'answer', '2': 'answer' ... }
    Returns an integer score (0-10).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("DEBUG: GEMINI_API_KEY not found in environment variables.", file=sys.stderr)
        return 0
        
    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Construct the context for grading
        grading_content = f"Skill: {skill_name}\n\n"
        for q in questions:
            q_id = str(q['id'])
            answer = user_answers.get(q_id, "No answer provided")
            grading_content += f"Q{q_id}: {q['question']}\nUser Answer: {answer}\n\n"
            
        prompt = f"""
        You are an expert evaluator for the skill: "{skill_name}".
        Grade the following assessment.
        There are 10 questions.
        The user provided short answers.
        
        {grading_content}
        
        Criteria:
        - Correctness of the concept relative to the skill domain.
        - Clarity.
        - Give 1 point for a correct answer, 0 for incorrect.
        
        Output strictly in JSON format:
        {{
            "score": <total_score_int>,
            "results": [
                {{
                    "question_id": 1,
                    "status": "correct" or "incorrect",
                    "correct_answer": "Brief correct answer or explanation"
                }},
                ...
            ]
        }}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        print(f"DEBUG: Gemini Grade Response: {response.text}", file=sys.stderr)
        
        data = json.loads(response.text)
        return data # Returns {'score': int, 'results': [...]}
        
    except Exception as e:
        print(f"DEBUG: Error grading quiz: {e}", file=sys.stderr)
        # Fallback to 0 if something breaks hard, or re-raise if we want to show error
        return {'score': 0, 'results': []}
