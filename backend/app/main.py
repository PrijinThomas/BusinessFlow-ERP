from fastapi import FastAPI

app = FastAPI(
    title="ERP Project API",
    description="Backend API for BusinessFlow ERP",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the BusinessFlow ERP API"}
