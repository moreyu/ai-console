"""
ID Token Generator Utility

Generates synthetic id_token from access_token for cliproxy compatibility.
Cliproxy requires id_token to extract chatgpt_account_id for quota display.
"""

import json
import base64
from typing import Optional


def create_id_token_from_access_token(access_token: str) -> str:
    """
    Create a synthetic id_token from an access_token.

    Extracts claims from the access_token JWT and constructs an id_token
    that contains the necessary auth information for cliproxy.

    Args:
        access_token: The OpenAI access token (JWT format)

    Returns:
        A synthetic id_token in JWT format (header.payload.)
    """
    # Decode access_token to extract claims
    parts = access_token.split('.')
    if len(parts) < 2:
        raise ValueError("Invalid access_token format")

    payload = parts[1]
    # Add padding if needed
    padding = '=' * ((4 - len(payload) % 4) % 4)
    decoded = base64.urlsafe_b64decode(payload + padding)
    claims = json.loads(decoded)

    # Extract auth information
    auth_info = claims.get('https://api.openai.com/auth', {})
    profile_info = claims.get('https://api.openai.com/profile', {})

    # Construct id_token payload with necessary claims
    id_token_payload = {
        "email": profile_info.get('email', ''),
        "https://api.openai.com/auth": auth_info,
        "exp": claims.get('exp'),
        "iat": claims.get('iat'),
        "iss": claims.get('iss', 'https://auth.openai.com'),
        "sub": claims.get('sub', '')
    }

    # Create JWT header (no signature needed for cliproxy)
    header = {
        "alg": "none",
        "typ": "JWT"
    }

    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip('=')

    payload_encoded = base64.urlsafe_b64encode(
        json.dumps(id_token_payload).encode()
    ).decode().rstrip('=')

    # Return JWT format: header.payload. (no signature)
    return f"{header_encoded}.{payload_encoded}."


def ensure_id_token(account) -> str:
    """
    Ensure account has an id_token, generating one if missing.

    Args:
        account: Account object with access_token and optional id_token

    Returns:
        The existing id_token or a newly generated one
    """
    if account.id_token:
        return account.id_token

    if account.access_token:
        return create_id_token_from_access_token(account.access_token)

    return ""
