from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None

    def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        print("Connected to MongoDB")

    def close(self):
        self.client.close()
        print("Disconnected from MongoDB")

    def get_master_db(self):
        return self.client[settings.DB_NAME]
    
    def get_collection(self, collection_name: str):
        
        
        
        return self.client[settings.DB_NAME][collection_name]

db = Database()