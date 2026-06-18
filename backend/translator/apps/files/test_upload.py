import requests


session = requests.Session()

session.post('http://127.0.0.1:8000/api/auth/login/', json={
    'username': 'kratos',
    'password': 'kratos12'
})


