from rest_framework.exceptions import APIException

class OneFeedbackAllowed(APIException):
    status_code = 403
    default_detail = 'You are only allowed one feedback per match'

class TwoPlayersPerMatch(APIException):
    status_code = 403
    default_detail = 'There are already 2 players registered for this match'

class SelfSignUp(APIException):
    status_code = 403
    default_detail = "You can't sign up for a match that you created"

class NoPlayerToConfirmOrDecline(APIException):
    status_code = 403
    default_detail = 'There is no player to decline'

class OnlyCreatorMayConfirmOrDecline(APIException):
    status_code = 403
    default_detail = 'Only the Match Creator may decline the matchup'