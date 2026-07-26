import requests
import json

prompt = """You are a Senior Product Researcher at Blinkit, a quick-commerce platform in India.
    
    ## GOAL
    Blinkit's north-star metric is: **Increase the % of Monthly Active Customers who purchase from >=1 new category every month.**
    
    You have a dataset (the review themes context) containing real user reviews with fields like id, channel, text, themes, discovery_role, interview_validation, etc.
    
    ## TASK
    Answer the 8 research questions below. For each question, produce exactly 2 to 3 highly impactful findings.
    
    ## RESEARCH QUESTIONS & THEME MAPPING
    Answer the 8 research questions below. You MUST strictly use the assigned Theme for each question.
    Question 1: Why do users repeatedly buy from the same categories? -> Map to Theme: "Delivery Speed & Reliability"
    Question 2: What prevents users from exploring new categories? -> Map to Theme: "Category Exploration Friction"
    
    ## RULES
    1. Only cite real reviews from the dataset. Use the 'id' field.
    2. Tag single-review findings with "(Single-review finding)".
    3. Tag interview-validated findings with "(Interview-confirmed)", "(Interview-challenged)", or "(New from interviews)".
    4. Prioritize Survey responses as primary evidence.
    5. Exactly 2 to 3 findings per question. No more, no less. Each finding must be distinct.
    6. Write "Why it matters" in terms of the north-star metric.
    
    CRITICAL INSTRUCTION: You MUST output ONLY a valid JSON array of objects. Do not include any markdown formatting or explanations outside the JSON array.
    
    The JSON array must follow this exact structure:
    [
      {
        "emoji": "🛒",
        "category": "[Theme Title from the data]",
        "questionNumber": "Question 1",
        "questionText": "Why do users repeatedly buy from the same categories?",
        "insightHeadline": "[One-line headline summary]",
        "findings": [
          {
            "findingNumber": "Finding 1",
            "observation": "[Clear statement.]",
            "evidence": "Review [id] [[channel]]: \\"[Exact quote]\\"",
            "impact": "[1-2 sentences impact]"
          }
        ]
      }
    ]
    
    CRITICAL JSON ESCAPING RULES:
    1. Escape any internal double quotes with a backslash (e.g., \\").
    2. Do NOT include unescaped newlines inside strings.
    3. Ensure there are no trailing commas.
    
    Ensure the output is strictly parseable JSON."""

resp = requests.post("http://localhost:8000/api/ask-groq", json={"prompt": prompt})
print(resp.text)
