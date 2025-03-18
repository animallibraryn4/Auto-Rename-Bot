import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.madflixbotz = self._client[database_name]
        self.col = self.madflixbotz.user

    def new_user(self, id):
        return dict(
            _id=int(id),                                   
            file_id=None,
            file_name=None,  # Stores File Name
            caption=None,
            format_template=None,
            metadata=None  # Stores Metadata
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)            
            await send_log(b, u)

    async def is_user_exist(self, id):
        """ Check if a user exists in the database. """
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def set_file_name(self, id, file_name):
        """ Store file name for a user. """
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_name': file_name}})

    async def get_file_name(self, id):
        """ Retrieve file name for a user. """
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_name', None)

    async def delete_file_name(self, id):
        """ Delete file name for a user. """
        await self.col.update_one({'_id': int(id)}, {'$unset': {'file_name': ""}})

    async def set_metadata(self, id, metadata):
        """ Store metadata for a user. """
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata': metadata}})

    async def get_metadata(self, id):
        """ Retrieve metadata for a user. """
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata', None)

    async def delete_metadata(self, id):
        """ Delete metadata for a user. """
        await self.col.update_one({'_id': int(id)}, {'$unset': {'metadata': ""}})

madflixbotz = Database(Config.DB_URL, Config.DB_NAME)
