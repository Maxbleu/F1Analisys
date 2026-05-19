import os, jwt
from fastapi import status, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Este método se encarga de obtener el token jwt
    pasado en la petición, para comprobar si
    es el correcto.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            os.environ["SECRET_KEY"],
            algorithms=[os.environ["ALGORITHM"]]
        )
        payload_id = str(payload.get("id")).strip().lower()
        payload_sub = str(payload.get("sub")).strip().lower()
        expected_id = os.environ["ID_PAYLOAD_JWT"].strip().lower()
        expected_sub = os.environ["SUB_PAYLOAD_JWT"].strip().lower()
        if payload_id != expected_id or payload_sub != expected_sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token inválido"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )