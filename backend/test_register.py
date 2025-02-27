import requests

# Registration endpoint
url = 'http://localhost:8000/auth/register'

# User credentials
user_data = {
    'username': 'fatakeshto',
    'password': 'Fatakeshto@123',  # Strong password that meets validation requirements
    'email': 'fatakeshto@example.com',
    'role': 'user'
}

# Attempt registration
response = requests.post(url, json=user_data)

# Print response
print(f'Status Code: {response.status_code}')
print(f'Response: {response.json()}')

# Example of a strong password that would pass validation:
# Fatakeshto@123
# This password contains:
# - Uppercase (F)
# - Lowercase (atakeshto)
# - Numbers (123)
# - Special character (@)
# - More than 8 characters