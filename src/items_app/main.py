from fastapi import FastAPI
import uvicorn
from items_app.api.routers import router


app = FastAPI()


@app.get("/healthy", summary="Проверка работы приложения", tags=["Healthcheck"])
async def healthcheck():
    return "Server is running"


app.include_router(router)


def main():
    uvicorn.run("__main__:app", host="127.0.0.1", port=8080, reload=True)


if __name__ == "__main__":
    main()
