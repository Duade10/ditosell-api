import uuid

from django.utils import timezone

from db_connection import db


class Shipment:
    """Shipment Model Class"""

    def __init__(self, shipment_dict):
        self.shipments = db["shipments"]

        if shipment_dict:
            self.category = shipment_dict["category"]
            self.item = shipment_dict["item"]
            self.weight = shipment_dict["weight"]
            self.quantity = shipment_dict["quantity"]
            self.sender_id = shipment_dict["sender_id"]
            self.receiver_id = shipment_dict["receiver_id"]
            try:
                self.image = shipment_dict["image"]
            except (AttributeError, KeyError):
                self.image = None
            try:
                self.user_id = shipment_dict["user_id"]
            except (AttributeError, KeyError):
                self.user_id = None

        else:
            self.category = None
            self.item = None
            self.weight = None
            self.quantity = None
            self.image = None
            self.user_id = None
            self.sender_id = None
            self.receiver_id = None

    def get_shipment(self, string_value=None, value=None) -> dict:
        """Takes the name of the field and a value of the shipment object and return the object"""

        if string_value:
            query = {string_value: value}

        shipment = self.shipments.find_one(query)

        if shipment:
            return {
                "category": shipment["category"],
                "item": shipment["item"],
                "weight": shipment["weight"],
                "quantity": shipment["quantity"],
                "image": shipment["image"],
            }
        return None

    def add_shipment(self) -> dict:
        """From the Shipment Dictionary supplied into the class Argument, it creates a new Shipment object."""

        custom_id = str(uuid.uuid4())

        new_shipment = {
            "id": custom_id,
            "category": self.category,
            "item": self.item,
            "weight": self.weight,
            "quantity": self.quantity,
            "image": self.image,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "user_id": self.user_id,
            "created_at": str(timezone.now()),
            "updated_at": None,
            "is_active": True,
        }

        self.shipments.insert_one(new_shipment).inserted_id
        new_shipment = self.get_shipment("id", new_shipment.get("id"))

        return new_shipment

    def update_shipment(self, shipment_id, shipment_dict) -> dict:
        """Takes the id of the shipment object and the shipment dict of the values to be updated"""

        self.shipments.update_one({"id": shipment_id}, {"$set": shipment_dict})
        shipment = self.get_shipment("id", shipment_id)

        return shipment
