from typing import Dict, Any, Set

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.uow import UnitOfWork
from core.dependencies import get_uow
from core.db import SessionLocal

from core.const import Role, TokenType
from auth.service import decode_jwt


security = HTTPBearer()


async def get_access_token_data(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    uow: UnitOfWork = Depends(get_uow)
) -> Dict[str, Any]:
    token = credentials.credentials
    data  = decode_jwt(token)
    
    if not data.get("type") == TokenType.ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not valid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    session_id = data.get("sid")
    
    if not uow.user_sessions.is_active(session_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return data


def require_role(allowed: Set[Role]):
    async def checker(token_data: Dict[str, Any] = Depends(get_access_token_data)):
        raw_roles: List[str] = token_data.get("roles", [])
        user_roles = {Role(r) for r in raw_roles if r in Role._value2member_map_}

        if not (user_roles & allowed):
            allowed_list = ", ".join(r.value for r in allowed)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {allowed_list}"
            )
        return token_data
    return checker

require_superadmin = require_role({Role.SUPERADMIN})
require_admin = require_role({Role.ADMIN, Role.SUPERADMIN})
require_editor = require_role({Role.EDITOR, Role.ADMIN, Role.SUPERADMIN})
require_viewer = require_role({Role.VIEWER, Role.EDITOR, Role.ADMIN, Role.SUPERADMIN})
require_member = require_role({Role.MEMBER, Role.VIEWER, Role.EDITOR, Role.ADMIN, Role.SUPERADMIN})
require_enduser = require_role({Role.ENDUSER})

