from fastapi import FastAPI
from app.routers import similarity_router

app = FastAPI(title="ATS Score Calculator", version="2.0")

# Register routers
app.include_router(similarity_router.router)