from typing import Optional
from pydantic import BaseModel, root_validator
from datetime import date


class CreateBlog(BaseModel):
    title: str
    slug: str
    category: str
    content: Optional[str] = None

    @root_validator(pre=True)
    # @model_validator(mode='before')
    def generate_slug(cls, values):
        if 'title' in values:
            values['slug'] = values.get("title").replace(" ", "-").lower()
        return values


class ShowBlog(BaseModel):
    title: str
    content: Optional[str]
    category: str
    created_at: date

    class Config():
        orm_mode = True


class UpdateBlog(CreateBlog):
    pass
