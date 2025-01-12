import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from typing import Any, Annotated


import tensorflow as tf
#from tensorflow.keras.datasets import mnist
from tensorflow import keras


from fastapi import FastAPI, Form
from fastapi import File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging


import psycopg2 as psy
from config import config

db = 'mnistdb'
table = 'data'


logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

logger.debug('error message')

app = FastAPI()

model = tf.keras.models.load_model('savedModels/test_model.keras')

origins = [
    'http://localhost:3001',
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']

)

def connectTest():
    

    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psy.connect(**config()) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psy.DatabaseError, Exception) as error:
        print(error)

def connect_Create_db():
    conn = None
    try:
        conn = psy.connect(**config())
        conn.autocommit = True
        print("Connected to the PostgreSQL server")

        crsr = conn.cursor()
        crsr.execute('SELECT version()')
        db_version = crsr.fetchone()
        #crsr.close()
        print(f"PostgreSQL database version: {db_version}")

        dbname = db
        #crsr.execute('CREATE DATABASE pycreatetest ;')
        #crsr.execute('SELECT datname FROM pg_database WHERE datistemplate = false;')
        crsr.execute(f"SELECT datname FROM pg_database WHERE datname = '{dbname}'")
        tables = crsr.fetchall()
        #print(len(tables))
        if len(tables) == 0:
            crsr.execute(f'CREATE DATABASE {dbname}')
        else:
            print('DB exists')
        crsr.close()

    except(Exception, psy.DatabaseError) as error:
        print(error)

    finally:
        if conn != None:
            conn.close()
            #print("Connection closed")

def create_table():
    '''
    Create postgres table to store images and data
    '''
    try:
        conn = psy.connect(**config(),database=db) #Hardcoded database choice, can be moved to ini later
        conn.autocommit = True
        crsr = conn.cursor()

        crsr.execute(f'''SELECT EXISTS ( SELECT FROM information_schema.tables WHERE table_name   = '{table}');''')
        
        exists = bool(crsr.fetchone()[0])
        if (exists == True):
            print('Table exists')
        else:
            crsr.execute(f'''CREATE TABLE {table} (id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, image TEXT, label INT, prediction INT, correct BOOL, certainty REAL);''')
            print('Table created')
        
    except(Exception, psy.DatabaseError) as error:
        print (error)

    finally:
        crsr.close()
        conn.close()

def load_to_postgres(path:str="numbers"):
    '''
    Load dataset from folder into postgresql table
    
    Parameters
    ----------
    
    path: (str) path to root folder containing dataset

    Returns
    ----------
    
    numbers: (ndarray) (n,24,24) Array of number images
    
    labels: (ndarray) (n,) Array of labels
    
    Folder structure
    -----------------
    
    /numbers #root dir
        numbers/0
            img.jpg
            img.jpg
            .
            .
            .
        numbers/1   
            img.jpg
            img.jpg
            .
            .
            .
        .
        .
        .
        
    numbers folder containing folders with folder name as the label (0 to 9)
    Image names within label folders not relevant
    '''
    try:
        conn = psy.connect(**config(),database=db)
        print(conn)
        conn.autocommit = True
        crsr=conn.cursor()
        for i in range(10):
            for dirpath,dirnames,filenames in (os.walk(f"{path}/{i}")):
                for file in filenames:
                    img = cv2.imread(f"{path}/{i}/{file}",cv2.IMREAD_GRAYSCALE) 
                    img = cv2.resize(img,(28,28), interpolation=cv2.INTER_AREA)
                    img = (255-img)/255.0
                    #img = np.reshape(img,(1,28,28))

                    temp_image = np.reshape(img,(-1)) #Image stored as a string (TEXT) of a 1D array in postgres
                    
                    crsr.execute(f'''INSERT INTO {table}(image, label) VALUES ('{temp_image}',{i})''')
        crsr.close()
    except(Exception, psy.DatabaseError) as error:
        print (error)
    finally:
        if conn != None:
            conn.close()
            print("Connection closed")
    
def predict_from_postgres(id):
    '''
    Predict number & uncertainty, display processed image, from postgres table

    Parameters
    ----------
    id (int): Primary key from postgres table
    '''
    try:
        conn = psy.connect(**config(),database=db) #Hardcoded database choice, can be moved to ini later
        conn.autocommit = True

        crsr = conn.cursor()
        crsr.execute(f'''SELECT image FROM {table} WHERE id = {id}''')
        data = str(crsr.fetchone()[0])

        crsr.execute(f'''SELECT label FROM {table} WHERE id = {id}''')
        label = crsr.fetchone()[0]

        #Image stored as a string (TEXT) of a 1D array in postgres convert to a np.ndarray
        img = (np.fromstring(data.strip('[]'),dtype=float, sep=' '))

        img = np.reshape(img, (1,28,28)) #Reshape image as model.predict requires 3D array

        prediction, certainty = show_img(0,img,[label])

        if (prediction != None) & (prediction == label):
            correct = True
        elif (prediction != label):
            correct = False
        
        #Update table values
        crsr.execute(f'''UPDATE {table} SET prediction = {prediction}, certainty = {certainty}, correct = {correct} WHERE id = {id}''')

        

    except(Exception, psy.DatabaseError) as error:
        print (error)

    finally:
        crsr.close()
        conn.close()

# for i in range(1,13):
#     predict_from_postgres(i)

def show_img(i, data, labels):
    '''
    Show image at index i of array of images
    '''
    plt.imshow((data)[i], cmap=plt.cm.binary)
    
    predA = (model.predict(data)[i])
    pred = np.argmax(predA)
    certainty = round((np.max(predA)*100),2)
    
    if (pred == labels[i]):
        color = 'green'
    else:
        color = 'red'
        
    plt.xlabel(f"Pred:{pred} (Actual:{labels[i]})", color=color)
    #plt.show()

    return(pred, certainty)
    
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

@app.post("/test")
def testUploadForm(file: Annotated[UploadFile, Form()], label: Annotated[str, Form()]):
    label = int(label)
    
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

    certainty = round(float(certainty), 2)

    #print(type(num))

    #os.remove(file.filename)

    num = np.reshape(num,(28,28))

    plt.imshow(num,cmap=plt.cm.binary)
    plt.xlabel(f"Prediction: {pred} with certainty {certainty}%")
    #plt.show()

    plt.savefig(file.filename)

    if (pred != None) & (pred == label):
            correct = True
    elif (pred != label):
        correct = False

    if label == 11:
        label = 'NULL'
        correct = 'NULL'

    #logger.debug('error message')
    
    connect_Create_db()
    create_table()
    try:
        conn = psy.connect(**config(),database=db)
        conn.autocommit = True
        crsr=conn.cursor()
        num = np.reshape(num,(-1))
        crsr.execute(f'''INSERT INTO {table}(image, label, prediction, correct, certainty) VALUES ('{num}', {label}, {pred}, {correct}, {certainty})''')
        crsr.execute(f'''SELECT MAX(id) FROM {table}''')
        data = crsr.fetchone()[0]
        crsr.close()
        message = 'yes'
        print (data)
    except(Exception, psy.DatabaseError) as error:
        print(error)
    finally:
        conn.close()

    #print(type(label), type(certainty)) 

    #certainty is numpy.float32, pred is numpy int64 --> numpy formats not json compatible must be standard types
    return (int(pred), float(certainty)) #

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

@app.get("/iNiTiAlIsE")
def iNiTiAlIsE():
    connect_Create_db()
    create_table()
    load_to_postgres()
    for i in range(1,13):
        predict_from_postgres(i)
    return("Done initialising")


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

logger.debug('end')
