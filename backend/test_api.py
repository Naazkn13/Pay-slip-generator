import requests

url = "http://127.0.0.1:5000/api/upload"
file_path = r"c:\Users\NuzhatKhan\Downloads\paySlip generator\excel\Emp pay sheet.xlsx"

try:
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(url, files=files)
        
    print(f"Status Code: {response.status_code}")
    print("Response Data (first 300 chars):", str(response.json())[:300])
except Exception as e:
    print("Error:", e)
