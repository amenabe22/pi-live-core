import os
import base64
import inspect
import phonenumbers
from typing import Type

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic import BaseModel

from sqlalchemy.inspection import inspect as sql_inspect
from sqlalchemy.orm.attributes import NO_VALUE

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def as_form(cls: Type[BaseModel]):
    new_params = [
        inspect.Parameter(
            "cls",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Type[BaseModel]
        )
    ]

    for field_name, model_field in cls.model_fields.items():
        default = model_field.default if not model_field.is_required() else ...
        ann = model_field.annotation
        new_params.append(
            inspect.Parameter(
                field_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Form(default),
                annotation=ann
            )
        )

    async def _as_form(cls, **data):
        try:
            return cls(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise RequestValidationError(e.errors())
            raise

    sig = inspect.signature(_as_form).replace(parameters=new_params)
    _as_form.__signature__ = sig  # type: ignore
    setattr(cls, "as_form", classmethod(_as_form))
    return cls

def country_code(s: str, default_region: str | None = None) -> str | None:
    try:
        n = phonenumbers.parse(s, default_region)
        return f"+{n.country_code}" if phonenumbers.is_valid_number(n) else None
    except phonenumbers.NumberParseException:
        return None

# -- cryptographic funcs--

CIPHER_VERSION = b"v1"
CIPHER_MIN_LEN = len(CIPHER_VERSION) + 16 + 12 + 16  # ver(2) + salt(16) + nonce(12) + tag(16)

def encrypt(
    data: str | bytes,
    key: str | bytes,
    aad: bytes | None = None,
) -> bytes:
    if isinstance(data, str):
        data = data.encode("utf-8")
    if isinstance(key, str):
        key = key.encode("utf-8")

    salt = os.urandom(16)
    nonce = os.urandom(12)

    kdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"aesgcm-key")
    k = kdf.derive(key)

    ct = AESGCM(k).encrypt(nonce, data, aad)
    return CIPHER_VERSION + salt + nonce + ct

def decrypt(
    token: bytes,
    key: str | bytes,
    aad: bytes | None = None,
) -> bytes:
    if isinstance(key, str):
        key = key.encode("utf-8")

    if len(token) < CIPHER_MIN_LEN:
        raise ValueError("ciphertext too short")

    ver = token[:2]
    if ver != CIPHER_VERSION:
        raise ValueError("bad version")

    salt = token[2:18]
    nonce = token[18:30]
    ct = token[30:]

    kdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"aesgcm-key")
    k = kdf.derive(key)

    return AESGCM(k).decrypt(nonce, ct, aad)

def encrypt_to_b64(
    data: str | bytes,
    key: str | bytes,
    aad: bytes | None = None,
) -> str | None:
    try:
        return base64.urlsafe_b64encode(encrypt(data, key, aad)).decode("ascii")
    except Exception:
        return None

def decrypt_from_b64(
    token_b64: str,
    key: str | bytes,
    aad: bytes | None = None,
) -> str | None:
    try:
        raw = base64.urlsafe_b64decode(token_b64.encode("ascii"))
        return decrypt(raw, key, aad).decode("utf-8")
    except Exception:
        return None

def orm_to_dict(
    obj, 
    *, 
    only_loaded: bool = False, 
    exclude=(), 
    _seen=None
):
  
    if obj is None:
        return None

    if isinstance(obj, (list, tuple, set)):
        return [
            orm_to_dict(
                x, 
                only_loaded=only_loaded, 
                exclude=exclude, 
                _seen=_seen
            ) 
            for x in obj
        ]

    insp = sql_inspect(obj)

    if _seen is None:
        _seen = set()
    
    key = (
        insp.identity_key 
        if insp.identity_key is not None 
        else (type(obj), id(obj))
    )
    
    if key in _seen:
        return None
    
    _seen.add(key)

    exclude = set(exclude)
    data = {}

    for col in insp.mapper.columns:
        if col.key in exclude:
    
            continue
        data[col.key] = getattr(obj, col.key)

    
    for rel in insp.mapper.relationships:
        if rel.key in exclude:
            continue
    
        if only_loaded and insp.attrs[rel.key].loaded_value is NO_VALUE:
            continue

        val = getattr(obj, rel.key)
        
        if val is None:
            data[rel.key] = None
        
        elif rel.uselist:
            data[rel.key] = [
            orm_to_dict(
                x, 
                only_loaded=only_loaded, 
                exclude=exclude, 
                _seen=_seen
            )
            for x in val
        ]
        else:
            data[rel.key] = orm_to_dict(
                val, 
                only_loaded=only_loaded, 
                exclude=exclude, 
                _seen=_seen
            )

    for k, v in vars(obj).items():
        if k.startswith("_"):
            continue
        if k in exclude:
            continue
        data.setdefault(k, v)      

    return data