"""Simplified Flask application with intentional issues for audit."""
from flask import Flask, request
import hashlib
import subprocess
import tempfile

app = Flask(__name__)
app.config['DEBUG'] = True  # B201: Debug mode enabled

# B303: Using MD5 (weak crypto)
SECRET_KEY = "hardcoded-secret-12345"  # Hardcoded secret

def validate_user(user_id):
    # B101: Using assert for validation
    assert user_id > 0, "Invalid user"
    return True

@app.route('/search', methods=['POST'])
def search():
    # B602: Shell injection vulnerability
    query = request.form.get('q')
    result = subprocess.run(f"grep -r {query} /tmp", shell=True)
    return result

@app.route('/hash', methods=['POST'])
def hash_password():
    password = request.form.get('password')
    # B303: MD5 hash (weak)
    hash_obj = hashlib.md5(password.encode())
    return {'hash': hash_obj.hexdigest()}

@app.route('/save', methods=['POST'])
def save_data():
    # B108: Hardcoded temp directory
    data = request.form.get('data')
    with open('/tmp/data.txt', 'w') as f:
        f.write(data)
    return 'Saved'

# E302: Missing blank lines
def another_function():
    pass
def yet_another():
    pass

# E501: Line too long
def process_data(user_id, username, email, phone, address, city, state, zipcode, country, organization):
    pass

# C901: High cyclomatic complexity
def complex_logic(a, b, c, d):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # B104: Bind to all interfaces
