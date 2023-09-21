import uuid

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
        self.senders = db["Senders"]

        if sender_dict:
            self.full_name = sender_dict["full_name"]
            self.phone_number = sender_dict["phone_number"]
            self.pickup_address = sender_dict["pickup_address"]
            self.region = sender_dict["region"]
            self.user_id = sender_dict["user_id"]
        else:
            self.full_name = None
            self.phone_number = None
            self.pickup_address = None
            self.region = None

        def get_sender(self, string_value=None, value=None):
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
                }
            return None

        def add_sender(self):
            custom_id = str(uuid.uuid4())
            new_sender = {
                "id": custom_id,
                "full_name": self.full_name,
                "phone_number": self.phone_number,
                "region": self.region,
            }
            self.senders.insert_one(new_sender).inserted_id
            new_sender = self.get_sender("id", self.id)
            return new_sender

        def update_sender(self, sender_id, sender_dict):
            self.senders.update_one({"id": sender_id}, {"$set": sender_dict})
            sender = self.get_sender("id", sender_id)
            return sender
