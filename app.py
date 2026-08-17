from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from routers import auth, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', status_code=200)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.get('/ola_mundo', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def ola_mundo():
    return """
    <html>
      <head>
        <title> Nosso olá mundo!</title>
      </head>
      <body>
        <h1> Olá Mundo </h1>
      </body>
    </html>"""
