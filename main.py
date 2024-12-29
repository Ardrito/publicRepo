import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow import keras

import matplotlib.pyplot as plt
import cv2
from fastapi import FastAPI

from fastapi import File

app = FastAPI()

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
    
    return(pred,certainty)

@app.get("/")
def welcome()-> str:
    return("Welcome")

@app.get("/2")
def welcome()-> str:
    return("Page 2")

from fastapi import File, UploadFile, HTTPException

#import aiofiles

@app.post("/upload")
def upload(file: UploadFile = File(...))-> tuple[int, float]:
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        file.file.close()
    
    num = cv2.imread(f"{file.filename}",cv2.IMREAD_GRAYSCALE) #Read the image as a grayscale
    pred, uncertainty = predict(num)

    return pred,uncertainty

    #return {"message": f"Successfully uploaded {file.filename}"}


#@app.post("/upload")
#async def endpoint(image: bytes = File()):
#    image = cv2.imread(image,cv2.IMREAD_GRAYSCALE)
#    show_img(image)