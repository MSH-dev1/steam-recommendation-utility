"""Steam OpenID 2.0 login flow, implemented manually (no auth library).

Reference: https://steamcommunity.com/dev (Steam-specific notes) and the
OpenID 2.0 spec (http://openid.net/specs/openid-authentication-2_0.html).
"""

import re

import httpx

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
OPENID_NS = "http://specs.openid.net/auth/2.0"
OPENID_IDENTIFIER_SELECT = "http://specs.openid.net/auth/2.0/identifier_select"

_CLAIMED_ID_RE = re.compile(r"^https://steamcommunity\.com/openid/id/(\d+)$")


def build_login_redirect_url(base_url: str) -> str:
    """Build the URL that redirects the user to Steam's OpenID login page."""
    params = {
        "openid.ns": OPENID_NS,
        "openid.mode": "checkid_setup",
        "openid.identity": OPENID_IDENTIFIER_SELECT,
        "openid.claimed_id": OPENID_IDENTIFIER_SELECT,
        "openid.realm": base_url,
        "openid.return_to": f"{base_url}/api/v1/auth/steam/callback",
    }
    query = httpx.QueryParams(params)
    return f"{STEAM_OPENID_URL}?{query}"


def verify_callback(params: dict[str, str]) -> bool:
    """Confirm with Steam that the callback parameters are genuine.

    Steam's reply must never be trusted on its own: we send the exact same
    openid.* parameters back to Steam (only openid.mode changes) and check
    that Steam confirms the assertion is valid.
    """
    verify_params = dict(params)
    verify_params["openid.mode"] = "check_authentication"

    response = httpx.post(STEAM_OPENID_URL, data=verify_params)
    response.raise_for_status()
    return "is_valid:true" in response.text


def extract_steam_id(claimed_id: str) -> str:
    """Pull the numeric SteamID64 out of an openid.claimed_id URL."""
    match = _CLAIMED_ID_RE.match(claimed_id)
    if not match:
        raise ValueError(f"Unexpected claimed_id format: {claimed_id!r}")
    return match.group(1)
