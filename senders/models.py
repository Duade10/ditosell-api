import uuid

from django.utils import timezone

from db_connection import db

REGION_TYPE_MAINLAND = "mainland"
REGION_TYPE_ISLAND = "island"

REGION_TYPE = (
    (REGION_TYPE_MAINLAND, "Mainland"),
    (REGION_TYPE_ISLAND, "Island"),
)


class Sender:
    """Sender Model Class"""

    def __init__(self, sender_dict=None):
        self.senders = db["senders"]

        if sender_dict:
            self.full_name = sender_dict["full_name"]
            self.phone_number = sender_dict["phone_number"]
            self.pickup_address = sender_dict["pickup_address"]
            self.region = sender_dict["region"]
            try:
                self.user_id = sender_dict["user_id"]
            except (AttributeError, KeyError):
                self.user_id = None
        else:
            self.full_name = None
            self.phone_number = None
            self.pickup_address = None
            self.region = None
            self.user_id = None

    def get_sender(self, string_value=None, value=None) -> dict:
        if string_value:
            query = {string_value: value}

        sender = self.senders.find_one(query)

        if sender:
            return {
                "id": sender["id"],
                "full_name": sender["full_name"],
                "phone_number": sender["phone_number"],
                "pickup_address": sender["pickup_address"],
                "region": sender["region"],
                "user_id": sender["user_id"],
                "created_at": sender["created_at"],
                "updated_at": sender["updated_at"],
                "is_active": sender["is_active"],
            }
        return None

    def add_sender(self) -> dict:
        """Takes Instiantiated Sender Dict as input and creates a Sender Object in the database"""

        custom_id = str(uuid.uuid4())
        new_sender = {
            "id": custom_id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "pickup_address": self.pickup_address,
            "region": self.region,
            "user_id": self.user_id,
            "created_at": str(timezone.now()),
            "updated_at": None,
            "is_active": True,
        }
        self.senders.insert_one(new_sender).inserted_id
        new_sender = self.get_sender("id", new_sender.get("id"))
        return new_sender

    def update_sender(self, sender_id, sender_dict) -> dict:
        """Takes Sender ID and QuerySet Object And Return Sender Object"""

        self.senders.update_one({"id": sender_id}, {"$set": sender_dict})
        sender = self.get_sender("id", sender_id)
        return sender
