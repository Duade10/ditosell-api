import uuid
from django.utils import timezone
from db_connection import db


class Payment:
    """Payment Model Class"""

    def __init__(self, payment_dict=None):
        self.payments = db["payments"]

        def check_field(string_value):
            try:
                obj = payment_dict[string_value]
                return obj
            except (AttributeError, KeyError):
                return None

        if payment_dict:
            self.id = check_field("id")
            self.reference = check_field("reference")
            self.currency = check_field("currency")
            self.amount = check_field("amount")
            self.amount_expected = check_field("amount_expected")
            self.fee = check_field("fee")
            self.status = check_field("status")
            self.payment_reference = check_field("payment_reference")
            self.transaction_status = check_field("transaction_status")
            self.created_at = check_field("created_at")
            self.updated_at = check_field("updated_at")
        else:
            self.id = None
            self.reference = None
            self.currency = None
            self.amount = None
            self.amount_expected = None
            self.fee = None
            self.status = None
            self.payment_reference = None
            self.transaction_status = None
            self.created_at = None
            self.updated_at = None

    def get_payment(self, string_value=None, value=None):
        if string_value:
            query = {string_value: value}

        payment = self.payments.find_one(query)

        if payment:
            return {
                "id": payment["id"],
                "reference": payment["reference"],
                "currency": payment["currency"],
                "amount": payment["amount"],
                "amount_expected": payment["amount_expected"],
                "fee": payment["fee"],
                "status": payment["status"],
                "payment_reference": payment["payment_reference"],
                "transaction_status": payment["transaction_status"],
                "created_at": payment["created_at"],
                "updated_at": payment["updated_at"],
            }

        return None

    def add_payment(self):
        custom_id = str(uuid.uuid4())

        new_payment = {
            "id": custom_id,
            "reference": self.reference,
            "currency": self.currency,
            "amount": self.amount,
            "amount_expected": self.amount_expected,
            "fee": self.fee,
            "status": self.status,
            "payment_reference": self.payment_reference,
            "transaction_status": self.transaction_status,
            "created_at": str(timezone.now().isoformat()),
            "updated_at": self.updated_at,
        }

        inserted_id = self.payments.insert_one(new_payment).inserted_id
        new_payment = self.get_payment("_id", inserted_id)

        return new_payment

    def update_payment(self, payment_id, payment_dict):
        self.payments.update_one({"id": payment_id}, {"$set": payment_dict})
        payment = self.get_payment("id", payment_id)

        return payment

    def delete_payment(self, payment_id):
        result = self.payments.delete_one({"id": payment_id})

        return result.deleted_count > 0
