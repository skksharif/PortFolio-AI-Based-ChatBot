from flask import Flask, request, jsonify, render_template
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyBVW0nIrXofWHIzZ5LbYsFWx-VrQlOBFrE")

# Initialize Flask app
app = Flask(__name__)

# Load QA data
with open('./dataset.json', 'r') as file:
    data = json.load(file)

questions = [item["question"] for item in data["qa_pairs"]]
answers = [item["answer"] for item in data["qa_pairs"]]

# Load model and create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
question_embeddings = model.encode(questions).astype('float32')

# Initialize FAISS index
embedding_dim = question_embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(question_embeddings)

# Function to get the top answer from FAISS
def get_top_answer_faiss(user_question):
    user_embedding = model.encode([user_question]).astype('float32')
    distances, indices = index.search(user_embedding, k=3)
    top_answer = answers[indices[0][0]]
    print(top_answer)
    return top_answer

# Function to enhance answer using Gemini API
import re

# List to store previous prompts
previous_prompts = []

def enhance_answer_with_gemini(user_question, base_answer):
    try:
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'howdy', 'hi there']
        if any(greeting in user_question.lower() for greeting in greetings):
            previous_prompts.append(f"Greeting: {user_question}")
            return "Hello! What Would you like to know about Sharif?"

        previous_prompts.append(f"Sharif question: {user_question}")
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        input_text = f"""
            Understand context of {user_question}.If {base_answer} is not matched with {user_question}.Answer on your own positively about sharif.
            0) User question context: {user_question}. Analyze this question in relation to Sharif and provide a fitting response.
            If the user asks about Sharif, enhance the answer using the base answer, and add more context, examples, and insights while keeping it concise and user-friendly.
            Example: Here is the base answer: '{base_answer}'. Enhance this response by adding more context, examples, and insights to make it detailed and helpful."        
            
"""

        gemini_response = gemini_model.generate_content(input_text)
    
        enhanced_answer = gemini_response.content
        return enhanced_answer

    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return base_answer

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get('question', '')
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    # Get base answer from FAISS
    base_answer = get_top_answer_faiss(user_question)
    enhanced_answer = enhance_answer_with_gemini(user_question, base_answer)
    return jsonify({"answer": enhanced_answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port or default to 5000
    app.run(host="0.0.0.0", port=port)
