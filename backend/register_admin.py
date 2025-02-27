import requests

# Registration endpoint
url = 'https://fatakeshto-application.onrender.com/auth/register'

# Admin user credentials
user_data = {
    'username': 'fatakeshto',
    'password': 'Fatakeshto@123',
    'email': 'fatakeshto@example.com',
    'role': 'admin'
}

# Attempt registration
try:
    response = requests.post(url, json=user_data)
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json()}')
    
    if response.status_code == 200 or response.status_code == 201:
        print('\nAdmin user successfully created!')
    else:
        print('\nFailed to create admin user. Please check the response details above.')
        
except requests.exceptions.RequestException as e:
    print(f'\nError occurred: {str(e)}')