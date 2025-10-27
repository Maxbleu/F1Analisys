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
            os.getenv("SECRET_KEY","41e9d1caf3d341f332d72f86b88592057dc9ef7e8cdccba74c904c976513d075f021ac0971817b50a3c6a99fff81cdb5de83885c3c85419cb3a33e54e8b98195"), 
            algorithms=[os.getenv("ALGORITHM","HS256")]
        )
        payload_id = str(payload.get("id")).strip().lower()
        payload_sub = str(payload.get("sub")).strip().lower()
        expected_id = os.getenv("ID_PAYLOAD_JWT","47}z2POZBJ|QNa!f:5l=q_qC{d(MmSK'A#o?4dw0GCf#Rpvf").strip().lower()
        expected_sub = os.getenv("SUB_PAYLOAD_JWT",";jrL3~vQ+KF76ai[:xZmU/x/ekW[i$pgK-C3BB197SqBO;z").strip().lower()
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