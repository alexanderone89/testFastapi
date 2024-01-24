from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import HTTPException, status
from typing import List

from db.models.user import User
from routes.route_login import get_current_user
from db.session import get_db
from schemas.blog import ShowBlog, CreateBlog, UpdateBlog
from db.repository.blog import (create_new_blog,
                                retreive_blog,
                                list_blogs,
                                update_blog,
                                delete_blog,
                                list_blogs_by_q
                                )
from typing import Annotated


router = APIRouter()


@router.post("/blog",response_model=ShowBlog, status_code=status.HTTP_201_CREATED)
def create_blog(blog: CreateBlog, db: Session= Depends(get_db), current_user: User= Depends(get_current_user)):

    blog = create_new_blog(blog=blog,db=db, author_id= current_user.id)
    return blog


@router.get("/blog/{id}", response_model=ShowBlog)
def get_blog(id: int, db: Session= Depends(get_db)):
    blog = retreive_blog(id=id, db=db)
    if not blog:
        raise HTTPException(detail=f"Blog with ID {id} does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    return blog


@router.get("/blogs", response_model=List[ShowBlog])
def get_all_blogs(db: Session = Depends(get_db)):

    blogs = list_blogs(db=db)
    return blogs


@router.get("/blogs/")
async def read_items(category: Annotated[str | None, Query(max_length=20)] = None, db: Session = Depends(get_db)):

    blogs = list_blogs_by_q(category, db)
    return blogs


@router.put("/blog/{id}", response_model=ShowBlog)
def update_a_blog(id: int, blog: UpdateBlog, db: Session = Depends(get_db), current_user: User=Depends(get_current_user)):
    blog = update_blog(id=id, blog=blog, author_id=current_user.id, db=db)
    if isinstance(blog,dict):
        raise HTTPException(
            detail=blog.get("error"),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return blog


@router.delete("/delete/{id}")
def delete_a_blog(id: int, db: Session = Depends(get_db), current_user: User=Depends(get_current_user)):
    message = delete_blog(id=id, author_id=current_user.id, db=db)
    if message.get("error"):
        raise HTTPException(
            detail=message.get("error"), status_code=status.HTTP_400_BAD_REQUEST
        )
    return {"msg": f"Successfully deleted blog with id {id}"}



