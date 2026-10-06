from fastapi import FastAPI

from services.repliers import get_listings


app = FastAPI(
    title="AI Home Finder API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Home Finder API is running"
    }


@app.get("/homes")
def homes():
    return get_listings()