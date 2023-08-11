"""
This module handles authentication logic for the promptguard chat server.
This logic is independent of the langchain integration, and is not needed
for other servers using the promptguard langchain integration.
"""
from http import HTTPStatus
from typing import Dict, List, Optional

import jwt
from fastapi import HTTPException


class VerifyToken:
    """
    Handles authentication token verification using PyJWT

    Logic for this class was derived from this blog
    https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/
    """

    domain = "opaque-ppp-dev.us.auth0.com"
    audience = "https://ppp-service.com"
    algorithms = ["RS256"]

    def __init__(self, token: str):
        """
        Parameters
        ----------
        token : str
            An authorization token which verify() will validate.
        """
        self.token = token

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self, required_scopes: Optional[List[str]] = None) -> None:
        """
        Validates that the token associated with this instance is of
        the correct form and contains the neccessary signatures to access
        this application. Also verifies that the token contains the
        `required_scopes`.

        Parameters
        ----------
        required_scopes : list of strings, optional
            A list of scopes that must be present in the token for validation
            to pass
        """
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=f"https://{self.domain}/",
            )
        except Exception as error:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=str(error)
            )

        # Check for required scopes
        self._verify_scopes(payload, required_scopes)

    def _verify_scopes(
        self,
        token_payload: Dict[str, str],
        required_scopes: Optional[List[str]],
    ) -> None:
        """
        Helper function which handles scope validation for an extracted
        `token_payload`

        Parameters
        ----------
        token_payload : Dict[str, str]
            The extracted payload of an authorization jwt token
        required_scopes : list of strings, optional
            A list of scopes that must be present in the token for validation
            to pass
        """
        if required_scopes:
            if token_payload.get("scope"):
                token_scopes = token_payload["scope"].split()
                for scope in required_scopes:
                    if scope not in token_scopes:
                        raise HTTPException(
                            status_code=HTTPStatus.UNAUTHORIZED,
                            detail=f"missing required scope '{scope}'",
                        )
            else:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail=f"""bearer token missing required
                    scopes {required_scopes}""",
                )
