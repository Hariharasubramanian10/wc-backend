1.  **Clone the Repository**
2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Variables:**
    Create a `.env` file in the root:
    ```
    MONGO_URL=mongodb://localhost:27017
    DB_NAME=master_org_db
    SECRET_KEY=change_this_secret
    ```
5.  **Run the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
6.  **Access Docs:**
    Go to `http://127.0.0.1:8000/docs` to test the APIs interactively.

## Architecture Diagran
```mermaid
graph TD
    Client[Client / Frontend]
    
    subgraph "Backend Service (FastAPI)"
        API[API Routes]
        Auth[Auth Middleware]
        Service[Organization Service - Class Based]
    end
    
    subgraph "Database Layer (MongoDB)"
        MasterDB[(Master DB)]
        MetaColl[Metadata Collection]
        AdminColl[Admin Users Collection]
        
        OrgColl1[Collection: org_clientA]
        OrgColl2[Collection: org_clientB]
    end

    Client -->|JSON Requests| API
    API --> Service
    API -->|Verify Token| Auth
    
    Service -->|Read/Write Metadata| MetaColl
    Service -->|Auth Check| AdminColl
    Service -->|Create/Drop/Rename| OrgColl1
    Service -->|Create/Drop/Rename| OrgColl2
    
    MetaColl -.-> MasterDB
    AdminColl -.-> MasterDB
    OrgColl1 -.-> MasterDB
    OrgColl2 -.-> MasterDB
```