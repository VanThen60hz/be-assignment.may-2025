# Entry point for FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models, routes
from .db import engine
from .mcp_server import app as mcp_app

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Messaging System API",
    description="Backend messaging system API for River Flow Solutions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router, prefix="/api/v1")
app.mount("/mcp", mcp_app)


@app.get("/")
async def root():
    return {"message": "Welcome to Messaging System API"}
