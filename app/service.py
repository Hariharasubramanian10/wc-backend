from fastapi import HTTPException, status
from app.database import db
from app.models import OrgCreateRequest, OrgUpdateRequest
from app.security import SecurityUtils
from bson import ObjectId

class OrganizationService:
    def __init__(self):
        self.master_db = db.get_master_db()
        self.org_meta_coll = self.master_db["organizations"]
        self.admin_coll = self.master_db["admins"]

    async def create_organization(self, data: OrgCreateRequest):
        
        existing = await self.org_meta_coll.find_one({"organization_name": data.organization_name})
        if existing:
            raise HTTPException(status_code=400, detail="Organization name already exists")

        existing_admin = await self.admin_coll.find_one({"email": data.email})
        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin email already registered")

        
        collection_name = f"org_{data.organization_name}"
        
        org_doc = {
            "organization_name": data.organization_name,
            "collection_name": collection_name,
            "admin_email": data.email,
            "created_at": str(ObjectId().generation_time)
        }
        
        
        org_result = await self.org_meta_coll.insert_one(org_doc)
        org_id = org_result.inserted_id

        
        admin_doc = {
            "email": data.email,
            "password_hash": SecurityUtils.get_password_hash(data.password),
            "org_id": org_id,
            "org_name": data.organization_name
        }
        await self.admin_coll.insert_one(admin_doc)

        
        
        dynamic_coll = db.get_collection(collection_name)
        await dynamic_coll.insert_one({"type": "config", "msg": "Organization initialized"})

        return {
            "organization_name": data.organization_name,
            "collection_name": collection_name,
            "admin_email": data.email,
            "message": "Organization created successfully"
        }

    async def get_organization(self, org_name: str):
        org = await self.org_meta_coll.find_one({"organization_name": org_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        
        return {
            "organization_name": org["organization_name"],
            "collection_name": org["collection_name"],
            "admin_email": org["admin_email"],
            "message": "Details fetched"
        }

    async def login_admin(self, email, password):
        admin = await self.admin_coll.find_one({"email": email})
        if not admin or not SecurityUtils.verify_password(password, admin['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token_data = {
            "sub": str(admin["_id"]),
            "email": admin["email"],
            "org_id": str(admin["org_id"]),
            "org_name": admin["org_name"]
        }
        token = SecurityUtils.create_access_token(token_data)
        return {"access_token": token, "org_id": str(admin["org_id"])}

    async def update_organization(self, data: OrgUpdateRequest, current_user: dict):
        
        org_id = ObjectId(current_user["org_id"])
        current_org = await self.org_meta_coll.find_one({"_id": org_id})
        
        if not current_org:
            raise HTTPException(status_code=404, detail="Organization not found")

        
        new_name = data.organization_name
        old_name = current_org["organization_name"]
        old_coll_name = current_org["collection_name"]
        new_coll_name = f"org_{new_name}"

        if new_name != old_name:
            
            dup_check = await self.org_meta_coll.find_one({"organization_name": new_name})
            if dup_check:
                raise HTTPException(status_code=400, detail="New organization name already exists")
            
            
            
            try:
                await self.master_db.command(
                    "renameCollection", 
                    f"{settings.DB_NAME}.{old_coll_name}", 
                    to=f"{settings.DB_NAME}.{new_coll_name}"
                )
            except Exception as e:
                
                pass

        
        new_hash = SecurityUtils.get_password_hash(data.password)
        await self.admin_coll.update_one(
            {"org_id": org_id},
            {"$set": {"email": data.email, "password_hash": new_hash, "org_name": new_name}}
        )

        
        await self.org_meta_coll.update_one(
            {"_id": org_id},
            {"$set": {
                "organization_name": new_name,
                "collection_name": new_coll_name,
                "admin_email": data.email
            }}
        )

        return {
            "organization_name": new_name,
            "collection_name": new_coll_name,
            "admin_email": data.email,
            "message": "Organization updated and data migrated"
        }

    async def delete_organization(self, org_name: str, current_user: dict):
        
        
        if current_user["org_name"] != org_name:
             raise HTTPException(status_code=403, detail="Not authorized to delete this organization")

        org = await self.org_meta_coll.find_one({"organization_name": org_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        coll_name = org["collection_name"]

        
        try:
            await self.master_db[coll_name].drop()
        except Exception:
            pass 

        
        await self.org_meta_coll.delete_one({"organization_name": org_name})
        await self.admin_coll.delete_one({"org_id": org["_id"]})

        return {"message": f"Organization {org_name} and its data deleted"}