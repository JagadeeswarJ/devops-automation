from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "FastAPI application"
    }


@app.get("/users")
def users():

    return {
        "users": []
    }
