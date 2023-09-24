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


class Logistic:
    """Logistics Model Class"""

    def __init__(self, logistic_dict=None) -> dict or None:
        self.logistics = db["logistics"]

        def check_field(string_value) -> dict or None:
            """
            Check if a field exists in the logistic_dict dictionary and return its value.

            :param string_value: The name of the field to check.
            :return: The value of the field if it exists, or None if it doesn't.
            """

            try:
                obj = logistic_dict[string_value]

                return obj
            except (AttributeError, KeyError):
                # If the field doesn't exist or an error occurs, return None
                return None

        if logistic_dict:
            self.id = check_field("id")
            if self.logo_image:
                path = self.logo_image
                public_id = self.name
                response = upload(path, public_id=public_id)
                self.logo_image = response.get("secure_url")
            self.name = check_field("name")
        else:
            self.id = None
            self.logo_image = None
            self.name = None

    def get_logistic(self, string_value=None, value=None) -> dict or None:
        """
        Retrieves a logistics object from the database based on the specified attribute and its value.

        :param string_value: The name of the attribute to search by (e.g., "id").
        :param value: The value to match when searching for the logistics object.
        :return: A dictionary containing the logistics object's attributes (or None if not found).
        """

        # Construct a query based on the provided attribute and value
        if string_value:
            query = {string_value: value}

        logistic = self.logistics.find_one(query)

        # If a logistics object is found, return a dictionary with selected attributes
        if logistic:
            return {
                "id": logistic["id"],
                "logo_image": logistic["logo_image"],
                "name": logistic["name"],
            }

        # If no logistics object is found, return None
        return None

    def add_logistic(self) -> dict:
        """
        Adds a new logistics object to the database.

        :return: The newly created logistics object.
        """

        # Generate a unique custom ID for the new logistics object
        custom_id = str(uuid.uuid4())

        new_logistic = {
            "id": custom_id,
            "logo_image": self.logo_image,
            "name": self.name,
            "created_at": str(timezone.now),
            "updated_at": None,
        }

        inserted_id = self.logistics.insert_one(new_logistic).inserted_id
        new_logistic = self.get_logistic("_id", inserted_id)

        return new_logistic

    def update_logistic(self, logistic_id, logistic_dict) -> dict:
        """
        Updates a logistics object with the specified ID using the provided logistic_dict.

        :param logistic_id: The ID of the logistics object to be updated.
        :param logistic_dict: A dictionary containing the values to be updated.
        :return: The updated logistics object.
        """

        self.logistics.update_one({"id": logistic_id}, {"$set": logistic_dict})
        logistic = self.get_logistic("id", logistic_id)

        return logistic
