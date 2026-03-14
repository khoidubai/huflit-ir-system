from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import search
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="HUFLIT AI Search API",
    description="Advanced RAG Pipeline API for HUFLIT student portal",
    version="1.0.0"
)

# Enable CORS parameters so our frontend in port 3000 can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. Change this for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(search.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "HUFLIT AI API is running properly"}
