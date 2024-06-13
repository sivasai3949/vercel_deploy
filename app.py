from flask import Flask, jsonify, request, session, render_template
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app.secret_key = os.getenv("SECRET_KEY")

# Initial questions
questions = [
    "Please provide your general information like name, city, state, country.",
    "Please provide your academic performance (grade, board, present percentage).",
    "What is your goal, financial position, and Which places are you interested in going to for studies?"
]

# Options to present after initial questions
options = [
    "Would you like a detailed roadmap to achieve your career goals considering your academics, financial status, and study locations?",
    "Do you want personalized career guidance based on your academic performance, financial status, and desired study locations?",
    "Do you need other specific guidance like scholarship opportunities, study programs, or financial planning?",
    "Other"
]

@app.route('/')
def home():
    session.clear()
    session['question_index'] = 0
    session['user_responses'] = []
    return render_template('chat.html', initial_question=questions[0])

@app.route('/api/process_chat', methods=['POST'])
def process_chat():
    user_input = request.json.get('user_input')
    if user_input:
        question_index = session.get('question_index', 0)
        if question_index < len(questions):
            session['user_responses'].append(user_input)
            question_index += 1
            session['question_index'] = question_index
            if question_index < len(questions):
                return jsonify({"response": questions[question_index]})
            else:
                options_html = render_template('chat.html', options=options)
                return jsonify({"response": chat_html})
        else:
            bot_response = get_ai_response(user_input)
            return jsonify({"response": bot_response})
    return jsonify({"error": "Invalid input"}), 400

def get_ai_response(input_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    # Add all user responses
    for response in session.get('user_responses', []):
        messages.append({"role": "user", "content": response})
    
    messages.append({"role": "user", "content": input_text})
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message['content']

if __name__ == '__main__':
    app.run(debug=True)
