import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow import keras

import matplotlib.pyplot as plt
import cv2
from fastapi import FastAPI

from fastapi import File, UploadFile, HTTPException

import os

from typing import Any
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import psycopg2

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

#import aiofiles
origins = [
    'http://localhost:3000'
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']

)

model = tf.keras.models.load_model('savedModels/test_model.keras')

def show_img(i, data, labels):
    '''
    Show image at index i of array of images
    '''
    plt.imshow((data)[i], cmap=plt.cm.binary)
    
    predA = (model.predict(data)[i])
    pred = np.argmax(predA)
    
    if (pred == labels[i]):
        color = 'green'
    else:
        color = 'red'
        
    plt.xlabel(f"Pred:{pred} (Actual:{labels[i]})", color=color)
    plt.show()
    
def plot_graph(num_rows, num_cols, data, labels):
  '''
  Plot a graph of num_rows x num_cols with image and prediction.
  xlabel green for correct predictions, red for incorrect
  
  Parameters
  ----------
  num_rows: (int) number of rows
  num_cols: (int) number of columns
  data: NDArray(float64) Array of images
  label: list[int] List of labels corresponding to images
  '''
  num_images = num_rows*num_cols
  plt.figure(figsize=(2*2*num_cols, 2*num_rows))
  for i in range(num_images):
    plt.subplot(num_rows, 2*num_cols, 2*i+1)
    show_img(i,data,labels)
  plt.tight_layout()
  plt.show()
  
def predict(num):
    '''
    Predict number within image
    Show image with xlabel of prediction and certainty
    
    Parameters
    ----------
    
    num: Greyscale ndarray of the image
    
    cv2.imread("{FILENAME}",cv2.IMREAD_GRAYSCALE) to read greyscale image to parse into function
    
    
    Returns
    ----------
    pred: (np int64) Predicted number
    
    Certainty (np float32) Certainty of prediction to 2dp 
    
    '''
    num = cv2.resize(num,(28,28), interpolation=cv2.INTER_AREA) #Compress image to MNIST format, INTER_AREA best interpolation for images, provides most accuarate representation
    
    #If White number on black background -> flip colors
    if (np.mean(num) >= 123):
        num = (255-num)
    
    num = num/255.0 #Normailse greyscale values 0 to 1

    plt.imshow(num, cmap=plt.cm.binary) #Show image with greyscale colormap
    
    num = np.reshape(num,(1,28,28)) #model.Predict requires 3D np array (1,28,28)
    
    predA = (model.predict(num))    #Predict probability values
    pred = np.argmax(predA)         #Select highest probability value label
    certainty = round((np.max(predA)*100),2)    #Select certainty to 2dp
    
    #xlabel imshow with prediction and certainty to 2dp
    plt.xlabel(f"Prediction: {pred}, Certainty: {format(certainty, '.2f')}")
    plt.xticks([])
    plt.yticks([])
    
    return(num,pred,certainty)

@app.get("/")
async def welcome()-> str:

    # jsonresp = jsonable_encoder("Welcome")
    # return JSONResponse(content=jsonresp)
    return("welcome")

@app.post("/upload")
def upload(file: UploadFile = File(...))-> tuple[list, int, float]:
    '''
    Take uploaded file and predict
    
    Parameters
    -----------
    file: (Tested for JPG) Image of any dimensions or color, preferably square like

    returns
    -----------

    tuple[prediction, certainty]
    '''
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        file.file.close()
    
    num = cv2.imread(f"{file.filename}",cv2.IMREAD_GRAYSCALE) #Read the image as a grayscale
    num, pred, certainty = predict(num)

    print(type(num))

    #os.remove(file.filename)

    num = np.reshape(num,(28,28))

    plt.imshow(num,cmap=plt.cm.binary)
    plt.xlabel(f"Prediction: {pred} with certainty {certainty}%")

    plt.savefig(file.filename)

    return num.tolist(),pred,certainty

@app.get("/get/{name}")
def download(name)-> FileResponse:
    '''
    Return processed image with prediction and certainty as xlabel
    '''
    return FileResponse(name, filename='test.png', media_type="png")

@app.delete("/delete/{name}")
def remove(name: str)->str:
    '''
    Delete user uploaded photo from local storage
    '''
    if not (os.path.isfile(name)):
        return ("File does not exist")
    os.remove(name)

    return("Done")