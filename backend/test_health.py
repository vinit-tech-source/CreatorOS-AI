import requests
import traceback
try:
    response = requests.get("http://127.0.0.1:8000/api/v1/health")
    print("Health:", response.status_code, response.text)
except Exception as e:
    traceback.print_exc()
