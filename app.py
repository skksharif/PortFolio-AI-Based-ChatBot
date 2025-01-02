from flask import Flask, request, jsonify, render_template
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Initialize Flask app
app = Flask(__name__)

# Load QA data
with open('sharif_qa_pairs.json', 'r') as file:
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

# Function to get the top answer
def get_top_answer_faiss(user_question):
    user_embedding = model.encode([user_question]).astype('float32')
    distances, indices = index.search(user_embedding, k=1)
    top_answer = answers[indices[0][0]]
    return top_answer

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get('question', '')
    if not user_question:
        return jsonify({"error": "No question provided"}), 400
    top_answer = get_top_answer_faiss(user_question)
    return jsonify({"answer": top_answer})

if __name__ == '__main__':
    app.run(debug=True)
