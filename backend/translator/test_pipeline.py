import requests
import time

session = requests.Session()

# 1. Get token
response = requests.post('http://127.0.0.1:8000/api/token/', json={
    'username': 'testuser',
    'password': 'testpass123'
})
print("Token response:", response.json())
token = response.json()['access']
session.headers.update({'Authorization': f'Bearer {token}'})

# 2. Upload file
with open('sample_files/book.pdf', 'rb') as f:
    response = session.post(
        'http://127.0.0.1:8000/api/file/',
        files={'file': f},
        data={'file_format': 'pdf'}
    )
print("Upload response:", response.json())
file_id = response.json()['id']

# 3. Create translation job
response = session.post(
    'http://127.0.0.1:8000/api/jobs/',
    json={
        'input_file': file_id,
        'source_lang': 'en',
        'target_lang': 'ur'
    }
)
print("Job response:", response.status_code, response.text)
job_id = response.json()['id']
print(f"Job ID: {job_id}")

# 4. Poll for status
while True:
    response = session.get(f'http://127.0.0.1:8000/api/jobs/{job_id}/')
    data = response.json()
    print("Status:", data)
    if data['status'] in ['done', 'failed']:
        break
    time.sleep(5)

# 5. Download translated PDF
if data['status'] == 'done':
    response = session.get(f'http://127.0.0.1:8000/api/jobs/{job_id}/download/')
    with open('translated_output.pdf', 'wb') as f:
        f.write(response.content)
    print("Downloaded! Check translated_output.pdf")
else:
    print("Job failed:", data)



response = session.post(
    'http://127.0.0.1:8000/api/jobs/',
    json={
        'input_file': file_id,
        'source_lang': 'en',
        'target_lang': 'ur'
    }
)
print("Status code:", response.status_code)
print("Raw response:", response.text)