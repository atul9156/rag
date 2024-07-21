import uvicorn
from pathlib import Path
from fastapi import FastAPI

from router.document import document_router
from router.conversation import conversation_router
from router.user import user_router

from dotenv import load_dotenv

app = FastAPI(title="Awesome RAG application")

app.include_router(document_router, prefix="", tags=["document_router"])
app.include_router(conversation_router, prefix="", tags=["conversation_router"])
app.include_router(user_router, prefix="", tags=["user_router"])


@app.on_event("startup")
async def load_env():
    env_path = Path(__file__).parent / "/.env"
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
