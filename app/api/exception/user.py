"""
    User Defined Exception
"""

class UserError(Exception):
    """ base error class """

class UserNotFoundError(UserError):
    """ error if user record not found """
    msg = "User not found"
    title = "USER_NOT_FOUND"

class UserDuplicateError(UserError):
    """ error if user record not found """
    msg = "User record already exist"
    title = "DUPLICATE_USER"

class OldRecordError(UserError):
    """ error if user try updating information but some fields aren't changed """

    def __init__(self, details):
        super().__init__(details)
        self.details = details

        self.msg = "Updated fields can't be same with the old one"
        self.title = "UNIQUE_FIELDS_REQUIRED"
