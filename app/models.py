from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgGetRequest(BaseModel):
    organization_name: str  

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OrgResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    message: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    org_id: str