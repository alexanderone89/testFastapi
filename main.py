from fastapi import FastAPI
from core.config import settings
from db.session import engine
from db.base import Base
from routes.base import api_router

from core.hashing import Hasher

from db.models.user import User
from db.models.blog import Blog
from typing import Any


from core.security import create_access_token

from starlette.requests import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend


def create_tables():
    Base.metadata.create_all(bind=engine)


def include_router(app):
    app.include_router(api_router)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    create_tables()
    include_router(app)

    return app


app = start_application()


# register ModelAdmin
# admin = Admin(app, engine)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:

        form = await request.form()
        username, password = form["username"], form["password"]
        if not username == "admin@admin.ru" and not password == "pass":
            return False

        access_token = create_access_token(data={"sub":  "admin@admin.ru"})
        request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.password]
    form_excluded_columns = [User.blogs]

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request):
        data['password'] = Hasher.get_password_hash(data.get('password'))


class BlogAdmin(ModelView, model=Blog):
    column_list = [Blog.id, Blog.title, Blog.slug, Blog.category, Blog.content]
    column_details_list = [Blog.id, Blog.title, Blog.slug, Blog.category, "user.address.zip_code"]
    form_ajax_refs = {
        "author": {
            "fields": ("id", "email"),
            "order_by": ("id",),
        }
    }

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
admin = Admin(app=app, authentication_backend=authentication_backend, engine=engine)

admin.add_view(UserAdmin)
admin.add_view(BlogAdmin)

