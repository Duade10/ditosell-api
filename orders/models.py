import uuid

from django.utils import timezone

from db_connection import db


class Order:
    """Order Model Class"""

    def __init__(self, order_dict=None):
        self.orders = db["orders"]

        def check_field(string_value) -> dict or None:
            """
            Check if a field exists in the order_dict dictionary and return its value.

            :param string_value: The name of the field to check.
            :return: The value of the field if it exists, or None if it doesn't.
            """

            try:
                obj = order_dict[string_value]

                return obj
            except (AttributeError, KeyError):
                # If the field doesn't exist or an error occurs, return None
                return None

        if order_dict:
            self.id = check_field("id")
            self.logistic_id = check_field("logistic_id")
            self.sender_id = check_field("sender_id")
            self.receiver_id = check_field("receiver_id")
            self.shipment_id = check_field("shipment_id")
            self.user_id = check_field("user_id")
            self.created_at = check_field("created_at")
            self.updated_at = check_field("updated_at")
            self.progress = check_field("progress")
            self.price = check_field("price")
            self.is_active = check_field("is_active")
        else:
            self.id = None
            self.logistic_id = None
            self.sender_id = None
            self.receiver_id = None
            self.shipment_id = None
            self.user_id = None
            self.created_at = None
            self.updated_at = None
            self.progress = None
            self.price = None
            self.is_active = None

    def get_order(self, string_value=None, value=None) -> dict or None:
        """
        Retrieves a orders object from the database based on the specified attribute and its value.

        :param string_value: The name of the attribute to search by (e.g., "id").
        :param value: The value to match when searching for the orders object.
        :return: A dictionary containing the orders object's attributes (or None if not found).
        """
        if string_value:
            query = {string_value: value}

        order = self.orders.find_one(query)

        if order:
            return {
                "id": order["id"],
                "logistic_id": order["logistic_id"],
                "sender_id": order["sender_id"],
                "receiver_id": order["receiver_id"],
                "shipment_id": order["shipment_id"],
                "user_id": order["user_id"],
                "price": order["price"],
                "progress": order["progress"],
                "is_active": order["is_active"],
                "created_at": order["created_at"],
                "updated_at": order["updated_at"],
            }

        return None

    def add_order(self) -> dict:
        """
        Adds a new orders object to the database.

        :return: The newly created orders object.
        """
        custom_id = str(uuid.uuid4())

        new_order = {
            "id": custom_id,
            "price": self.price,
            "logistic_id": self.logistic_id,
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
        """
        Updates a orders object with the specified ID using the provided order_dict.

        :param order_id: The ID of the orders object to be updated.
        :param order_dict: A dictionary containing the values to be updated.
        :return: The updated orders object.
        """
        self.orders.update_one({"id": order_id}, {"$set": order_dict})
        order = self.get_order("id", order_id)
        return order
