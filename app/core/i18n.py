"""Minimal dict-based i18n: two languages, no build step.

A small translation dict per language is enough for en/ru. If this ever needs
pluralization or many more languages, switch to Babel/gettext - not worth the
build-step overhead at this scale.
"""

from collections.abc import Callable

from fastapi import Request

SUPPORTED_LANGUAGES = {"en", "ru"}
DEFAULT_LANGUAGE = "en"
LANGUAGE_COOKIE = "lang"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "nav.recommendations": "Recommendations",
        "nav.library": "Library",
        "nav.login": "Login with Steam",
        "nav.logout": "Logout",
        "landing.title": "Steam Recommendation Utility",
        "landing.description": (
            "Get game recommendations based on what you actually play - "
            "your library, your playtime, your taste in genres and tags."
        ),
        "landing.cta": "Login with Steam",
        "landing.view_recommendations": "View your recommendations",
        "footer.rawg_attribution": "Game data provided by RAWG (rawg.io)",
        "footer.copyright": "Steam Recommendation Utility",
    },
    "ru": {
        "nav.recommendations": "Рекомендации",
        "nav.library": "Библиотека",
        "nav.login": "Войти через Steam",
        "nav.logout": "Выйти",
        "landing.title": "Steam Recommendation Utility",
        "landing.description": (
            "Рекомендации игр на основе того, во что вы реально играете - "
            "ваша библиотека, наигранные часы, любимые жанры и теги."
        ),
        "landing.cta": "Войти через Steam",
        "landing.view_recommendations": "Смотреть рекомендации",
        "footer.rawg_attribution": "Данные об играх предоставлены RAWG (rawg.io)",
        "footer.copyright": "Steam Recommendation Utility",
    },
}


def resolve_language(request: Request) -> str:
    """Pick the active language: cookie > Accept-Language > default.

    An explicit user choice (the lang cookie) always wins. Otherwise, fall
    back to the browser's preferred language, then to English.
    """
    cookie_lang = request.cookies.get(LANGUAGE_COOKIE)
    if cookie_lang in SUPPORTED_LANGUAGES:
        return cookie_lang

    accept_language = request.headers.get("accept-language", "")
    if _prefers_russian(accept_language):
        return "ru"

    return DEFAULT_LANGUAGE


def _prefers_russian(accept_language: str) -> bool:
    """True if Russian is the top-ranked language in Accept-Language."""
    if not accept_language:
        return False
    top_choice = accept_language.split(",")[0].strip().split(";")[0].strip().lower()
    return top_choice.startswith("ru")


def get_translator(lang: str) -> Callable[[str], str]:
    """Return a t(key) function closed over the given language's dict."""
    translations = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])

    def t(key: str) -> str:
        return translations.get(key, key)

    return t
