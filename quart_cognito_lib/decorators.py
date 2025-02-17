from functools import wraps
from typing import Iterable
from quart import redirect, request, session, current_app
from quart_cognito_lib.config import Config
from quart_cognito_lib.utils import (
    generate_code_challenge,
    generate_code_verifier,
    secure_random,
)

cfg = Config()


def _cognito_auth():
    return current_app.extensions[cfg.APP_EXTENSION_KEY]


def remove_from_session(keys: Iterable[str]):
    """Remove an entry from the session"""
    for key in keys:
        if key in session:
            session.pop(key)


def cognito_login(fn):
    """A decorator that redirects to the Cognito hosted UI"""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        # store parameters in the session that are passed to Cognito
        # and required for JWT verification
        code_verifier = generate_code_verifier()
        cognito_session = {
            "code_verifier": code_verifier,
            "code_challenge": generate_code_challenge(code_verifier),
            "nonce": secure_random(),
        }
        session.update(cognito_session)

        # Add suport for custom state values which are appended to a secure
        # random value for additional CRSF protection
        state = secure_random()
        custom_state = session.get("state", None)
        if custom_state:
            state += f"__{custom_state}"

        session.update({"state": state})

        login_url = _cognito_auth().cognito_service.get_sign_in_url(
            code_challenge=session["code_challenge"],
            state=session["state"],
            nonce=session["nonce"],
            scopes=cfg.cognito_scopes,
        )

        return redirect(login_url)

    return wrapper


def cognito_login_callback(fn):
    """
    A decorator to wrap the redirect after a user has logged in with Cognito.
    Stores the Cognito JWT in a http only cookie.
    """

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        # Get the access token return after auth flow with Cognito
        code_verifier = session["code_verifier"]
        state = session["state"]
        nonce = session["nonce"]

        # exchange the code for an access token
        # also confirms the returned state is correct
        tokens = await _cognito_auth().get_tokens(
            request_args=request.args,
            expected_state=state,
            code_verifier=code_verifier,
        )

        # validate the JWT and get the claims
        claims = _cognito_auth().verify_access_token(
            token=tokens.access_token,
            leeway=cfg.cognito_expiration_leeway,
        )
        session.update({"claims": claims})

        # Grab the user info from the user endpoint and store in the session
        if tokens.id_token is not None:
            user_info = _cognito_auth().verify_id_token(
                token=tokens.id_token,
                nonce=nonce,
                leeway=cfg.cognito_expiration_leeway,
            )
            session.update({"user_info": user_info})

        # Remove one-time use variables now we have completed the auth flow
        remove_from_session(("code_challenge", "code_verifier", "nonce"))

        # split out the random part of the state value (in case the user
        # specified their own custom state value)
        state = session.get("state").split("__")[-1]
        session.update({"state": state})

        # return and set the JWT as a http only cookie
        resp = await fn(*args, **kwargs)

        # Store the access token in a HTTP only secure cookie
        resp.set_cookie(
            key=cfg.COOKIE_NAME,
            value=tokens.access_token,
            max_age=cfg.max_cookie_age_seconds,
            httponly=True,
            secure=True,
        )

        return resp

    return wrapper


def cognito_logout(fn):
    """A decorator that handles logging out with Cognito"""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        # logout at cognito and remove the cookies
        resp = redirect(cfg.logout_endpoint)
        resp.delete_cookie(key=cfg.COOKIE_NAME)

        # Cognito will redirect to the sign-out URL (if set) or else use
        # the callback URL
        return resp

    return wrapper
