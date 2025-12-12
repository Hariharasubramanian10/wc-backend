from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from jose import jwt, JWTError

from app.database import db
from app.service import OrganizationService
from app.models import (
    OrgCreateRequest, OrgResponse, OrgGetRequest, 
    OrgUpdateRequest, LoginRequest, TokenResponse
)
from app.config import settings

app = FastAPI(title="Org Management Service")


@app.on_event("startup")
async def startup_db_client():
    db.connect()

@app.on_event("shutdown")
async def shutdown_db_client():
    db.close()


def get_service():
    return OrganizationService()


async def get_current_admin(authorization: Annotated[str, Header()] = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Token")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload 
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")



@app.post("/org/create", response_model=OrgResponse)
async def create_org(
    data: OrgCreateRequest, 
    service: OrganizationService = Depends(get_service)
):
    return await service.create_organization(data)

@app.get("/org/get", response_model=OrgResponse)
async def get_org(
    organization_name: str, 
    service: OrganizationService = Depends(get_service)
):
    return await service.get_organization(organization_name)

@app.put("/org/update", response_model=OrgResponse)
async def update_org(
    data: OrgUpdateRequest,
    current_user: dict = Depends(get_current_admin),
    service: OrganizationService = Depends(get_service)
):
    return await service.update_organization(data, current_user)

@app.delete("/org/delete")
async def delete_org(
    organization_name: str, 
    current_user: dict = Depends(get_current_admin),
    service: OrganizationService = Depends(get_service)
):
    return await service.delete_organization(organization_name, current_user)

@app.post("/admin/login", response_model=TokenResponse)
async def admin_login(
    data: LoginRequest,
    service: OrganizationService = Depends(get_service)
):
    return await service.login_admin(data.email, data.password)