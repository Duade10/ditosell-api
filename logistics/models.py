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
            if check_field("image"):
                path = check_field("image")
                public_id = check_field("name")
                response = upload(path, public_id=public_id)
                self.image = response.get("secure_url")
            self.name = check_field("name")
        else:
            self.id = None
            self.image = None
            self.name = None

    def filter_logistic(self, string_value=None, value=None):
        """
        Filter and retrieve logistic data from the database.

        :param string_value: The name of the attribute to filter by (optional).
        :param value: The value to match when filtering (optional).
        :return: A cursor to the retrieved logistic data.
        """
        query = {}

        if string_value and value:
            query = {string_value: value}

        result = list(self.logistics.find(query))
        return result

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
                "image": logistic["image"],
                "name": logistic["name"],
                "is_active": logistic["is_active"],
                "created_at": logistic["created_at"],
                "updated_at": logistic["updated_at"],
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
            "image": self.image,
            "name": self.name,
            "created_at": str(timezone.now()),
            "updated_at": None,
            "is_active": True,
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

        if "image" in logistic_dict:
            path = logistic_dict["image"]
            public_id = logistic_dict["name"]
            response = upload(path, public_id=public_id)
            logistic_dict["image"] = response.get("secure_url")

        self.logistics.update_one({"id": logistic_id}, {"$set": logistic_dict})
        logistic = self.get_logistic("id", logistic_id)

        return logistic


class LogisticRate:
    """LogisticRate Model Class"""

    def __init__(self, logistic_rate_dict=None) -> dict or None:
        self.logistic_rates = db["logistic_rates"]

        def check_field(string_value) -> dict or None:
            """
            Check if a field exists in the logistic_rate_dict dictionary and return its value.

            :param string_value: The name of the field to check.
            :return: The value of the field if it exists, or None if it doesn't.
            """

            try:
                obj = logistic_rate_dict[string_value]
                return obj
            except (AttributeError, KeyError):
                return None

        if logistic_rate_dict:
            self.id = check_field("id")
            self.from_region = check_field("from_region")
            self.to_region = check_field("to_region")
            self.price = check_field("price")
            self.logistic_id = check_field("logistic_id")
            self.created_at = check_field("created_at")
            self.updated_at = check_field("updated_at")
        else:
            self.id = None
            self.from_region = None
            self.to_region = None
            self.price = None
            self.logistic_id = None
            self.created_at = None
            self.updated_at = None

    def filter_logistic_rate(self, string_value=None, value=None):
        """
        Filter and retrieve logistic rate data from the database.

        :param string_value: The name of the attribute to filter by (optional).
        :param value: The value to match when filtering (optional).
        :return: A cursor to the retrieved logistic rate data.
        """
        query = {}

        if string_value and value:
            query = {string_value: value}

        result = list(self.logistic_rates.find(query))
        return result

    def get_logistic_rate(self, string_value=None, value=None) -> dict or None:
        """
        Retrieves a logistic rate object from the database based on the specified attribute and its value.

        :param string_value: The name of the attribute to search by (e.g., "id").
        :param value: The value to match when searching for the logistic rate object.
        :return: A dictionary containing the logistic rate object's attributes (or None if not found).
        """

        if string_value:
            query = {string_value: value}

        logistic_rate = self.logistic_rates.find_one(query)

        if logistic_rate:
            return {
                "id": logistic_rate["id"],
                "from_region": logistic_rate["from_region"],
                "to_region": logistic_rate["to_region"],
                "price": logistic_rate["price"],
                "logistic_id": logistic_rate["logistic_id"],
                "created_at": logistic_rate["created_at"],
                "updated_at": logistic_rate["updated_at"],
            }

        # If no logistic rate object is found, return None
        return None

    def get_logistics_rate_price(self, from_region=None, to_region=None, logistic_id=None):
        query = {"from_region": from_region, "to_region": to_region, "logistic_id": logistic_id}

        logistic_rates = self.logistic_rates.find(query)

        results = []
        for logistic_rate in logistic_rates:
            results.append(
                {
                    "id": logistic_rate["id"],
                    "from_region": logistic_rate["from_region"],
                    "to_region": logistic_rate["to_region"],
                    "price": logistic_rate["price"],
                    "logistic_id": logistic_rate["logistic_id"],
                    "created_at": logistic_rate["created_at"],
                    "updated_at": logistic_rate["updated_at"],
                }
            )

        return results

    def add_logistic_rate(self) -> dict:
        """
        Adds a new logistic rate object to the database.

        :return: The newly created logistic rate object.
        """

        custom_id = str(uuid.uuid4())

        new_logistic_rate = {
            "id": custom_id,
            "from_region": str(self.from_region),
            "to_region": str(self.to_region),
            "price": self.price,
            "logistic_id": self.logistic_id,
            "created_at": timezone.now().isoformat(),
            "updated_at": None,
        }

        inserted_id = self.logistic_rates.insert_one(new_logistic_rate).inserted_id
        new_logistic_rate = self.get_logistic_rate("_id", inserted_id)

        return new_logistic_rate

    def update_logistic_rate(self, logistic_rate_id, logistic_rate_dict) -> dict:
        """
        Updates a logistic rate object with the specified ID using the provided logistic_rate_dict.

        :param logistic_rate_id: The ID of the logistic rate object to be updated.
        :param logistic_rate_dict: A dictionary containing the values to be updated.
        :return: The updated logistic rate object.
        """

        self.logistic_rates.update_one({"id": logistic_rate_id}, {"$set": logistic_rate_dict})
        logistic_rate = self.get_logistic_rate("id", logistic_rate_id)

        return logistic_rate

    def delete_logistic_rate(self, logistic_rate_id) -> bool:
        """
        Deletes a logistic rate object from the database.

        :param logistic_rate_id: The ID of the logistic rate object to be deleted.
        :return: True if the object was deleted successfully, False otherwise.
        """

        result = self.logistic_rates.delete_one({"id": logistic_rate_id})

        return result.deleted_count > 0
