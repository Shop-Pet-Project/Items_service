from fastapi import FastAPI
import uvicorn
from items_app.api.routers.healthcheck_routers import router as healthcheck_routers
from items_app.api.routers.companies_routers import router as companies_routers
from items_app.api.routers.items_routers import router as items_routers
from items_app.api.routers.auth_routers import router as auth_routers


app = FastAPI()

app.include_router(healthcheck_routers)
app.include_router(auth_routers)
app.include_router(companies_routers)
app.include_router(items_routers)


def main():
    uvicorn.run("__main__:app", host="127.0.0.1", port=8080, reload=True)


if __name__ == "__main__":
    main()
