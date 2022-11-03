from fastapi import FastAPI
 

from test1 import calapi

app = FastAPI()


@app.get("/")
def start():
    calapi()
    return "Succes"
    