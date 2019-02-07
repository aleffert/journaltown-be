from typing import List


class ResponseError:

    def __init__(self, code, errors):
        self.code = code
        self.errors = errors

    def render(self):
        return {'status': 'error', 'errors': self.errors, 'type': self.code}


class MissingFieldsError(ResponseError):

    def __init__(self, fields: List[str]):
        super().__init__('missing-fields', [
            {
                'message': f"Missing value for '{field}'",
                'name': field
            } for field in fields
        ])


class InvalidFieldsError(ResponseError):

    def __init__(self, fields: List[str]):
        super().__init__('invalid-fields', [
            {
                'message': f"Invalid value for '{field}'",
                'name': field
            } for field in fields
        ])


class EmailInUseError(ResponseError):

    def __init__(self):
        super().__init__('email-in-use', ['There is an already an account with that email address'])


class InvalidUsernameError(ResponseError):

    def __init__(self, name: str):
        super().__init__('unknown-username', [f"There is no user named '{name}'"])
