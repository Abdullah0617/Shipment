from contextlib import asynccontextmanager
from rich import print,panel
from fastapi import FastAPI


@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    print(panel.Panel("Server Started...",border_style="green"))
    yield
    print(panel.Panel("....stopped!!",border_style="red"))

app = FastAPI(lifespan=lifespan_handler)

@app.get("/")
def read_root():
    return {"details": "server running"}