"""
Flask API example - real code for testing
"""
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# INTENTIONAL ISSUES FOR TESTING:
# 1. Hardcoded secret (bandit should catch)
API_KEY = "sk-1234567890abcdef"  # Security issue!

# 2. Missing error handling
# 3. Long function (complexity issue)
@app.route('/api/process', methods=['POST'])
def process_data():
    data = request.get_json()
    user_id = data['user_id']  # No validation!
    query = data.get('query', '')

    # Simulate complex logic (radon should flag)
    if user_id == 1:
        result = "admin"
    elif user_id == 2:
        result = "user"
    elif user_id == 3:
        result = "guest"
    elif user_id == 4:
        result = "moderator"
    elif user_id == 5:
        result = "developer"
    elif user_id == 6:
        result = "tester"
    else:
        result = "unknown"

    # SQL injection vulnerable (bandit should catch)
    sql_query = f"SELECT * FROM users WHERE id = {user_id}"  # Dangerous!

    return jsonify({
        "status": "success",
        "result": result,
        "query": sql_query
    })

@app.route('/health')
def health():
    return "OK"

# Missing proper error handling
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # Security issue: debug in production
