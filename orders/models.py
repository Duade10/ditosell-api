import uuid

from django.utils import timezone

from db_connection import db


class Order:
    """Order Model Class"""

    def __init__(self, order_dict=None):
        self.orders = db["orders"]

        def check_field(string_value):
            try:
                obj = order_dict[string_value]
                return obj
            except (AttributeError, KeyError):
                return None

        if order_dict:
            self.id = check_field("id")
            self.logistics = check_field("logistics")
            self.sender_id = check_field("sender_id")
            self.receiver_id = check_field("receiver_id")
            self.shipment_id = check_field("shipment_id")
            self.user_id = check_field("user_id")
            self.created_at = check_field("created_at")
            self.updated_at = check_field("updated_at")
            self.progress = check_field("progress")
            self.is_active = check_field("is_active")
        else:
            self.id = None
            self.logistics = None
            self.sender_id = None
            self.receiver_id = None
            self.shipment_id = None
            self.user_id = None
            self.created_at = None
            self.updated_at = None
            self.progress = None
            self.is_active = None

    def get_order(self, string_value=None, value=None) -> dict:
        if string_value:
            query = {string_value: value}

        order = self.orders.find_one(query)

        if order:
            return {
                "id": order["id"],
                "logistics": order["logistics"],
                "sender_id": order["sender_id"],
                "receiver_id": order["receiver_id"],
                "shipment_id": order["shipment_id"],
                "user_id": order["user_id"],
                "created_at": order["created_at"],
                "updated_at": order["updated_at"],
                "progress": order["progress"],
                "is_active": order["is_active"],
            }

        return None

    def add_order(self) -> dict:
        custom_id = str(uuid.uuid4())

        new_order = {
            "id": custom_id,
            "logistics": self.logistics,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "user_id": self.user_id,
            "shipment_id": self.shipment_id,
            "created_at": str(timezone.now()),
            "updated_at": self.updated_at,
            "progress": "received",
            "is_active": True,
        }

        self.orders.insert_one(new_order).inserted_id
        new_order = self.get_order("id", new_order.get("id"))
        return new_order

    def update_order(self, order_id, order_dict) -> dict:
        """Takes order ID and QuerySet Dict And Return order Object"""

        self.orders.update_one({"id": order_id}, {"$set": order_dict})
        order = self.get_order("id", order_id)
        return order
