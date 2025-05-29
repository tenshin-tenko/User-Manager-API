from fastapi import FastAPI
from .routes.user_routes import user_router
from .routes.admin_routes import admin_router
from .routes.auth_rotes import auth_router

app = FastAPI(title='User Manager API')
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(auth_router)

@app.get('/')
async def root():
    return {'msg': 'running'}