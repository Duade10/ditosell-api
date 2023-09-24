import uuid

import cloudinary
from cloudinary.uploader import upload
from decouple import Csv, config
from django.utils import timezone

from db_connection import db

cloudinary.config(
    cloud_name=config("CLOUD_NAME"),
    api_key=config("API_KEY"),
    api_secret=config("API_SECRET"),
)


class Shipment:
    """Shipment Model Class"""

    def __init__(self, shipment_dict=None):
        self.shipments = db["shipments"]

        def check_field(string_value) -> dict or None:
            """
            Check if a field exists in the shipment_dict dictionary and return its value.

            :param string_value: The name of the field to check.
            :return: The value of the field if it exists, or None if it doesn't.
            """

            try:
                obj = shipment_dict[string_value]

                return obj
            except (AttributeError, KeyError):
                # If the field doesn't exist or an error occurs, return None
                return None

        if shipment_dict:
            self.category = shipment_dict["category"]
            self.item = shipment_dict["item"]
            self.weight = shipment_dict["weight"]
            self.quantity = shipment_dict["quantity"]
            self.sender_id = shipment_dict["sender_id"]
            self.receiver_id = shipment_dict["receiver_id"]
            try:
                path = shipment_dict["image"]
                public_id = f"{self.category}|{self.item}|{str(timezone.now())}"
                response = upload(path, public_id=public_id)
                self.image = response.get("secure_url")
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

    def get_shipment(self, string_value=None, value=None) -> dict or None:
        """
        Retrieves a shipments object from the database based on the specified attribute and its value.

        :param string_value: The name of the attribute to search by (e.g., "id").
        :param value: The value to match when searching for the shipments object.
        :return: A dictionary containing the shipments object's attributes (or None if not found).
        """
        if string_value:
            query = {string_value: value}

        shipment = self.shipments.find_one(query)

        # If a shipment object is found, return a dictionary with selected attributes
        if shipment:
            return {
                "id": shipment["id"],
                "category": shipment["category"],
                "item": shipment["item"],
                "weight": shipment["weight"],
                "quantity": shipment["quantity"],
                "image": shipment["image"],
                "sender_id": shipment["sender_id"],
                "receiver_id": shipment["receiver_id"],
                "user_id": shipment["user_id"],
                "created_at": shipment["created_at"],
                "updated_at": shipment["updated_at"],
                "is_active": shipment["is_active"],
            }

        # If no shipments object is found, return None
        return None

    def add_shipment(self) -> dict:
        """
        Adds a new shipments object to the database.

        :return: The newly created shipments object.
        """
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
        """
        Updates a shipments object with the specified ID using the provided shipment_dict.

        :param shipment_id: The ID of the shipments object to be updated.
        :param shipment_dict: A dictionary containing the values to be updated.
        :return: The updated shipments object.
        """
        self.shipments.update_one({"id": shipment_id}, {"$set": shipment_dict})
        shipment = self.get_shipment("id", shipment_id)

        return shipment
