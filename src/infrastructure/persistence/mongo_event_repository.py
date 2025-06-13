from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from bson import ObjectId # For converting string IDs to MongoDB ObjectId

from src.domain.entities.event import Event
from src.domain.repositories.event_repository import EventRepository

# A simple in-memory store for now to simulate MongoDB behavior without a live connection
# This will be replaced by actual MongoDB interaction.
# IN_MEMORY_DB: Dict[str, Dict[str, Any]] = {}

class MongoEventRepository(EventRepository):
    """
    MongoDB implementation of the EventRepository interface.
    """
    def __init__(self, database_url: str, database_name: str, collection_name: str = "events"):
        self._client: AsyncIOMotorClient = AsyncIOMotorClient(database_url)
        self._db: AsyncIOMotorDatabase = self._client[database_name]
        self._collection: AsyncIOMotorCollection = self._db[collection_name]
        # It's good practice to create indexes if they don't exist
        # asyncio.create_task(self._create_indexes()) # Requires async context or proper event loop handling at init

    # async def _create_indexes(self):
    #     await self._collection.create_index([("title", 1)]) # Example index

    async def save(self, event: Event) -> Event:
        """
        Saves an event to MongoDB. If event.id is None, it's an insert. Otherwise, it's an update.
        MongoDB uses '_id' for its primary key.
        """
        event_dict = event.model_dump(by_alias=True) # Uses alias '_id' for 'id'

        if event.id is None:
            # Insert new event
            # MongoDB will generate an _id if not provided
            if "_id" in event_dict and event_dict["_id"] is None:
                del event_dict["_id"] # Let MongoDB generate it

            result: InsertOneResult = await self._collection.insert_one(event_dict)
            event.id = str(result.inserted_id) # Update event model with the new ID
            return event
        else:
            # Update existing event
            event_id_obj = ObjectId(event.id)
            # Ensure '_id' is not part of the update payload if it's already used in filter
            update_data = {k: v for k, v in event_dict.items() if k != '_id'}

            result: UpdateResult = await self._collection.update_one(
                {"_id": event_id_obj},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                raise ValueError(f"Event with id {event.id} not found for update.")
            # Optionally, re-fetch the event to return the updated version from DB
            # For now, returning the input event, assuming update was successful on DB fields
            return event

    async def find_by_id(self, event_id: str) -> Optional[Event]:
        """
        Finds an event by its ID from MongoDB.
        """
        try:
            event_id_obj = ObjectId(event_id)
        except Exception: # Invalid ObjectId format
            return None

        document = await self._collection.find_one({"_id": event_id_obj})
        if document:
            # Pydantic model_validate will map _id to id if alias is set
            return Event.model_validate(document)
        return None

    async def find_all(self) -> List[Event]:
        """
        Returns all events from MongoDB.
        """
        events_cursor = self._collection.find()
        events_list = []
        async for document in events_cursor:
            events_list.append(Event.model_validate(document))
        return events_list

    async def delete_by_id(self, event_id: str) -> bool:
        """
        Deletes an event by its ID from MongoDB.
        Returns True if deleted, False otherwise.
        """
        try:
            event_id_obj = ObjectId(event_id)
        except Exception: # Invalid ObjectId format
            return False

        result: DeleteResult = await self._collection.delete_one({"_id": event_id_obj})
        return result.deleted_count > 0

    # Helper to close connection, useful for cleanup in tests or app shutdown
    async def close_connection(self):
        self._client.close()
