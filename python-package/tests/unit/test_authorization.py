"""
Unit tests for authorization.py
"""
import json
import os
from typing import Dict, List

import pytest
import requests
from fastapi.exceptions import HTTPException
from opchatserver.authorization import VerifyToken

### Fixtures ###


@pytest.fixture(scope="session")
def prompt_guard_test_secret() -> str:
    client_secret = os.environ.get("OPAQUEPROMPTS_TEST_SECRET")
    if not client_secret:
        pytest.fail(
            "OPAQUEPROMPTS_TEST_SECRET environment variable must be set for"
            "this test"
        )
    return client_secret  # type: ignore


@pytest.fixture(scope="session")
def auth0_access_token(prompt_guard_test_secret: str) -> str:
    headers: Dict[str, str] = {
        "content-type": "application/x-www-form-urlencoded"
    }
    data: Dict[str, str] = {
        "client_id": "Dk4QObdUPC2pFTkNJENiK0mmxBR3ubaE",
        "client_secret": prompt_guard_test_secret,
        "audience": VerifyToken.audience,
        "grant_type": "client_credentials",
    }
    user_auth_response_payload = json.loads(
        requests.post(
            f"https://{VerifyToken.domain}/oauth/token",
            headers=headers,
            data=data,
        ).text
    )
    if user_auth_response_payload.get("error"):
        pytest.fail(
            """
            Failed to get auth0 access token fromOPAQUEPROMPTS_TEST_SECRET,
            please ensure the value is correct
            """
        )
    return user_auth_response_payload.get("access_token")


### Tests ###


@pytest.mark.parametrize(
    "required_scopes",
    [
        None,
        [],
        ["use:opaque-ppp-chat-bot"],
    ],
    ids=[
        "no-required-scopes",
        "empty-required-scopes",
        "present-required-scopes",
    ],
)
def test_verify_success(
    required_scopes: List[str], auth0_access_token: str
) -> None:
    """
    Validates that VerifyToken.verify works as expected with
    a correct token
    """
    ########## ARRANGE ##########
    token_verifier = VerifyToken(auth0_access_token)

    ########## ACT ##########
    # No error should be thrown
    token_verifier.verify(required_scopes)


@pytest.mark.parametrize(
    "token",
    [
        "",
        "token",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxM"
        "jM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2"
        "MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    ],
    ids=["missing-token", "invalid-format", "invalid-token"],
)
def test_verify_invalid_token(token: str) -> None:
    """
    Validates that VerifyToken.verify throws an error when the provided token
    is incorrect or missing
    """
    ########## ARRANGE ##########
    token_verifier = VerifyToken(token)

    ########## ACT & ASSERT ##########
    with pytest.raises(HTTPException):
        token_verifier.verify()


@pytest.mark.parametrize(
    "required_scopes",
    [
        ["missing-scope"],
        ["use:opaque-ppp-chat-bot", "extra-missing-scope"],
    ],
    ids=["incorrect-scope", "mix-of-correct-and-incorrect-scopes"],
)
def test_verify_invalid_scopes(
    required_scopes: List[str], auth0_access_token: str
) -> None:
    """
    Validates that VerifyToken.verify throws an error when the provided token
    is valid, but does not have the required scopes
    """
    ########## ARRANGE ##########
    token_verifier = VerifyToken(auth0_access_token)

    ########## ACT & ASSERT ##########
    with pytest.raises(HTTPException):
        token_verifier.verify(required_scopes=required_scopes)


def test_verify_invalid_audience(auth0_access_token: str) -> None:
    """
    Validates that VerifyToken.verify throws an error when the provided token
    is a valid form, but doesn't have the right audience
    """
    ########## ARRANGE ##########
    token_verifier = VerifyToken(auth0_access_token)
    token_verifier.audience = "https://different-audience.com"

    ########## ACT & ASSERT ##########
    with pytest.raises(HTTPException):
        token_verifier.verify()


def test_verify_invalid_domain(auth0_access_token: str) -> None:
    """
    Validates that VerifyToken.verify throws an error when the provided token
    is a valid form, but doesn't have the right domain
    """
    ########## ARRANGE ##########
    token_verifier = VerifyToken(auth0_access_token)
    token_verifier.domain = "different-domain.us.auth0.com"

    ########## ACT & ASSERT ##########
    with pytest.raises(HTTPException):
        token_verifier.verify()
