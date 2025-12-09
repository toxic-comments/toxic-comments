from fastapi import FastAPI
import history, forward

app = FastAPI()

app.include_router(forward.router)
app.include_router(history.router)