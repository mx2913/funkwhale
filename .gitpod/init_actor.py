import subprocess
import requests

INSTANCE_URL = subprocess.check_output(['gp', 'url', '8000']).decode()[:-1]

# Login to initialize user actor
req = requests.Session()

res = req.get(INSTANCE_URL + '/login')
token = res.cookies['csrftoken']

req.post(INSTANCE_URL + '/api/v1/users/login', data={
    'username': 'gitpod',
    'password': 'gitpod'
}, headers={
    'Referer': INSTANCE_URL + '/login',
    'X-CSRFTOKEN': token
})

req.get(INSTANCE_URL)