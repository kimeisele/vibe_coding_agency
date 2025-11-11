"""
Example code to test KDAF validation tools.
This intentionally has issues for testing.
"""
import subprocess

# Security issue: hardcoded password
PASSWORD = "admin123"

# Complexity issue: god function
def process_user_data(name, email, age, address, phone, role, department, salary):
    """Process user data with many responsibilities"""
    # Missing error handling
    user_dict = {}
    user_dict['name'] = name
    user_dict['email'] = email
    user_dict['age'] = age
    user_dict['address'] = address
    user_dict['phone'] = phone
    user_dict['role'] = role
    user_dict['department'] = department
    user_dict['salary'] = salary

    # Shell injection vulnerability
    cmd = f"echo {name}"
    subprocess.call(cmd, shell=True)

    # Magic numbers
    if age > 65:
        user_dict['status'] = 'senior'
    elif age > 18:
        user_dict['status'] = 'adult'
    else:
        user_dict['status'] = 'minor'

    # More complexity
    if salary > 100000:
        user_dict['tax_bracket'] = 'high'
    elif salary > 50000:
        user_dict['tax_bracket'] = 'medium'
    else:
        user_dict['tax_bracket'] = 'low'

    return user_dict

# Unused variable
x = 10

def another_function():
    # Missing docstring
    pass
