import requests

# Login to initialize user actor
req = requests.Session()

res = req.get('http://localhost:8000/login')
token = res.cookies['csrftoken']

req.post('http://localhost:8000/api/v1/users/login', data={
    'username': 'gitpod',
    'password': 'gitpod'
}, headers={
    'Referer': 'http://localhost:8000/login',
    'X-CSRFTOKEN': token
})

req.get('http://localhost:8000')