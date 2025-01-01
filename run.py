import requests

import matplotlib.pyplot as plt

from PIL import Image
from io import BytesIO

#print (requests.get("http://127.0.0.1:8000/").json())



url = 'http://127.0.0.1:8000/upload'
file = {'file': open('numbers2/0.jpg', 'rb')}
resp = requests.post(url=url, files=file) 

num, pred, certainty = (resp.json())

print(pred, certainty)

#plt.imshow(num, cmap=plt.cm.binary)
#plt.xlabel(f"Prediction: {pred} with certainty {certainty}%")

name = "test.png"
get = requests.get(url=f"http://127.0.0.1:8000/get/{name}")

i = Image.open(BytesIO(get.content))

#with open("newTest.jpg", 'wb') as f:
#            f.write(get.content)

plt.imshow(i,)
plt.axis('off')
plt.show()

delname = "newTest.jpg"
print(requests.delete(f"http://127.0.0.1:8000/delete/{name}").json()) 
