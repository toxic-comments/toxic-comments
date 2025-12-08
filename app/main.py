from fastapi import FastAPI
from routers import forward, history

app = FastAPI()

app.include_router(forward.router)
app.include_router(history.router)