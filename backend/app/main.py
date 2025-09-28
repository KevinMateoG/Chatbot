from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import Union
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import uvicorn

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.post("/chat")
def chat(message: Message):
    # Aquí iría tu lógica de procesamiento del mensaje
    return {"response": f"Respuesta a: {message.message}"}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
    #hola mundo