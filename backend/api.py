from fastapi import FastAPI

app = FastAPI(
    title="AI Home Finder API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Home Finder API is running"
    }