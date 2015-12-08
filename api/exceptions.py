from rest_framework.exceptions import APIException

class OneFeedbackAllowed(APIException):
    status_code = 403
    default_detail = 'You are only allowed one feedback per match'