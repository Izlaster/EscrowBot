from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router

app = FastAPI()

origins = ["http://localhost", "https://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="")
