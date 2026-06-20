"""HTML pages (Jinja2 + Pico.css), separate from the JSON API under /api/v1."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.deps import get_current_user, get_language
from app.core.i18n import SUPPORTED_LANGUAGES, LANGUAGE_COOKIE, get_translator
from app.models.user import User

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def index(
    request: Request,
    lang: str = Depends(get_language),
    user: User | None = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"lang": lang, "t": get_translator(lang), "user": user},
    )


@router.get("/set-lang/{lang}")
def set_language(lang: str, request: Request) -> RedirectResponse:
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"

    redirect_to = request.headers.get("referer", "/")
    response = RedirectResponse(redirect_to)
    response.set_cookie(LANGUAGE_COOKIE, lang)
    return response
