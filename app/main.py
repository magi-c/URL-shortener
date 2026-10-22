from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .utils import generate_code

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")


def to_info(url: models.URL, request: Request) -> schemas.URLInfo:
    return schemas.URLInfo(
        short_code=url.short_code,
        target_url=url.target_url,
        short_url=str(request.base_url) + url.short_code,
        clicks=url.clicks,
        created_at=url.created_at,
    )


def get_url_or_404(code: str, db: Session) -> models.URL:
    url = db.scalar(select(models.URL).where(models.URL.short_code == code))
    if url is None:
        raise HTTPException(status_code=404, detail=f"Short code '{code}' not found")
    return url


@app.post("/shorten", response_model=schemas.URLInfo, status_code=status.HTTP_201_CREATED)
def create_short_url(payload: schemas.URLCreate, request: Request, db: Session = Depends(get_db)):
    if payload.custom_code:
        exists = db.scalar(select(models.URL).where(models.URL.short_code == payload.custom_code))
        if exists:
            raise HTTPException(status_code=409, detail="That short code is already taken")
        code = payload.custom_code
    else:
        code = generate_code()
        while db.scalar(select(models.URL).where(models.URL.short_code == code)):
            code = generate_code()  # extremely rare collision: try again

    url = models.URL(short_code=code, target_url=str(payload.target_url))
    db.add(url)
    db.commit()
    db.refresh(url)
    return to_info(url, request)


@app.get("/{code}")
def redirect_to_target(code: str, db: Session = Depends(get_db)):
    url = get_url_or_404(code, db)
    url.clicks += 1
    db.commit()
    return RedirectResponse(url.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/stats/{code}", response_model=schemas.URLInfo)
def get_stats(code: str, request: Request, db: Session = Depends(get_db)):
    return to_info(get_url_or_404(code, db), request)


@app.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_short_url(code: str, db: Session = Depends(get_db)):
    url = get_url_or_404(code, db)
    db.delete(url)
    db.commit()