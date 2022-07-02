import requests

# Login to initialize user actor
req = requests.Session()

res = req.get('http://localhost:8000/login')
print(res.status_code, res.cookies)
token = res.cookies['csrftoken']

res = req.post('http://localhost:8000/api/v1/users/login', data={
    'username': 'gitpod',
    'password': 'gitpod',
    'csrfmiddlewaretoken': token,
    'next': '/api/v1/libraries/?scope=me'
})
print(res.status_code, res.content)

if res.status_code == 401:
    exit(1)