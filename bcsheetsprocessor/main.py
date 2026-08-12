import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from bcsheetsprocessor.config import TEMPLATES_DIR
from bcsheetsprocessor.route import page_route, result_route, upload_route

app = FastAPI(title="Processador de Excel - BotConversa")

app.mount("/img", StaticFiles(directory=str(TEMPLATES_DIR / "img")), name="images")
app.mount("/templates", StaticFiles(directory=str(TEMPLATES_DIR)), name="templates-static")

app.include_router(page_route.router)
app.include_router(upload_route.router)
app.include_router(result_route.router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)