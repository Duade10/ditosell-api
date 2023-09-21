from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import BaseValidator

import re


class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError("The password must contain at least one uppercase letter.")

    def get_help_text(self):
        return "The password must contain at least one uppercase letter."


class CustomSimilarityValidator(BaseValidator):
    def __init__(self, user_attributes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_attributes = user_attributes or []

    def validate(self, password, user=None):
        if not user:
            return

        for attribute in self.user_attributes:
            if attribute and re.search(re.escape(attribute), password, re.IGNORECASE):
                raise ValidationError(
                    f"The password must not contain characters from your {attribute}.",
                    code="password_too_similar",
                )
