import requests

print (requests.get("http://127.0.0.1:8000/2").json())



url = 'http://127.0.0.1:8000/upload'
file = {'file': open('numbers2/0.jpg', 'rb')}
resp = requests.post(url=url, files=file) 
print(resp.json())7git 