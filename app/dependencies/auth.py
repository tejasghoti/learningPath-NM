# app/dependencies/auth.py
import os
import json
import urllib.request
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.utils import base64url_decode
from dotenv import load_dotenv

load_dotenv()

COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")

security = HTTPBearer()

# Cache the JWKS keys so we don't refetch on every request
_JWKS_CACHE = None

def get_cognito_jwks():
    global _JWKS_CACHE
    if _JWKS_CACHE is not None:
        return _JWKS_CACHE

    if not COGNITO_USER_POOL_ID:
        # If no Cognito pool is configured, return None to allow dummy auth for local testing
        return None

    jwks_url = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    try:
        with urllib.request.urlopen(jwks_url) as response:
            _JWKS_CACHE = json.loads(response.read().decode("utf-8"))
            return _JWKS_CACHE
    except Exception as e:
        print(f"Failed to fetch JWKS from Cognito: {e}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    FastAPI dependency that validates the JWT token provided in the Authorization header.
    It fetches the public keys from Amazon Cognito and verifies the token signature.
    """
    token = credentials.credentials

    # 1. Check if Cognito is configured. If not, bypass for local development/testing.
    if not COGNITO_USER_POOL_ID:
        print("WARNING: Cognito is not configured. Accepting all dummy tokens.")
        return {"sub": "dummy_user", "username": "local_tester"}

    # 2. Extract the JWT Headers to find the key ID (kid)
    try:
        headers = jwt.get_unverified_headers(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token format")

    kid = headers.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Invalid token headers")

    # 3. Get the JWKS from Cognito
    jwks = get_cognito_jwks()
    if not jwks:
        raise HTTPException(status_code=500, detail="Unable to retrieve Cognito keys")

    # 4. Find the correct public key for this token
    key_index = -1
    for i in range(len(jwks["keys"])):
        if kid == jwks["keys"][i]["kid"]:
            key_index = i
            break

    if key_index == -1:
        raise HTTPException(status_code=401, detail="Public key not found in Cognito JWKS")

    public_key = jwk.construct(jwks["keys"][key_index])
    message, encoded_signature = str(token).rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    # 5. Verify Signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        raise HTTPException(status_code=401, detail="Signature verification failed")

    # 6. Verify Claims (expiration, client_id)
    try:
        claims = jwt.get_unverified_claims(token)
        
        # Optionally verify client ID (Cognito tokens use 'client_id' for access tokens and 'aud' for id tokens)
        if COGNITO_CLIENT_ID:
            token_client_id = claims.get("client_id") or claims.get("aud")
            if token_client_id != COGNITO_CLIENT_ID:
                raise HTTPException(status_code=401, detail="Token was not issued for this audience/client_id")
                
        # Check token expiration
        import time
        if time.time() > claims.get("exp", 0):
            raise HTTPException(status_code=401, detail="Token is expired")
            
        return claims

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid claims: {str(e)}")
