from fastapi import FastAPI

app = FastAPI()


@app.get('/', status_code=200)
def read_root():
    return {'message': 'Olá Mundo!'}
