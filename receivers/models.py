import uuid

from django.utils import timezone

from db_connection import db

REGION_TYPE_MAINLAND = "mainland"
REGION_TYPE_ISLAND = "island"

REGION_TYPE = (
    (REGION_TYPE_MAINLAND, "Mainland"),
    (REGION_TYPE_ISLAND, "Island"),
)


class Receiver:
    """Receiver Model Class"""

    def __init__(self, receiver_dict=None):
        self.receivers = db["receivers"]

        if receiver_dict:
            self.full_name = receiver_dict["full_name"]
            self.phone_number = receiver_dict["phone_number"]
            self.pickup_address = receiver_dict["pickup_address"]
            self.region = receiver_dict["region"]
            self.sender_id = receiver_dict["sender_id"]
            try:
                self.user_id = receiver_dict["user_id"]
            except (AttributeError, KeyError):
                self.user_id = None

        else:
            self.full_name = None
            self.phone_number = None
            self.pickup_address = None
            self.region = None
            self.user_id = None
            self.sender_id = None

    def get_receiver(self, string_value=None, value=None) -> dict:
        if string_value:
            query = {string_value: value}

        receiver = self.receivers.find_one(query)

        if receiver:
            return {
                "id": receiver["id"],
                "full_name": receiver["full_name"],
                "phone_number": receiver["phone_number"],
                "pickup_address": receiver["pickup_address"],
                "region": receiver["region"],
                "user_id": receiver["user_id"],
                "sender_id": receiver["sender_id"],
            }
        return None

    def add_receiver(self) -> dict:
        """Takes Instiantiated Receiver Dict as input and creates a Receiver Object in the database"""

        custom_id = str(uuid.uuid4())
        new_receiver = {
            "id": custom_id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "pickup_address": self.pickup_address,
            "region": self.region,
            "user_id": self.user_id,
            "sender_id": self.sender_id,
            "created_at": str(timezone.now()),
            "updated_at": None,
            "is_active": True,
        }
        self.receivers.insert_one(new_receiver).inserted_id
        new_receiver = self.get_receiver("id", new_receiver.get("id"))
        return new_receiver

    def update_receiver(self, receiver_id, receiver_dict) -> dict:
        """Takes receiver ID and QuerySet Object And Return receiver Object"""

        self.receivers.update_one({"id": receiver_id}, {"$set": receiver_dict})
        receiver = self.get_receiver("id", receiver_id)
        return receiver
