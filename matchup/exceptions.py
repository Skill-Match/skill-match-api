from rest_framework.exceptions import APIException

# Exceptions for Improper Use of API


class OneFeedbackAllowed(APIException):
    status_code = 400
    default_detail = 'You are only allowed one feedback per player per match'


class TwoPlayersPerMatch(APIException):
    status_code = 400
    default_detail = 'There are already 2 players registered for this match'


class SelfSignUp(APIException):
    status_code = 400
    default_detail = "You can't sign up for a match that you created"


class NoPlayerToConfirmOrDecline(APIException):
    status_code = 400
    default_detail = 'There is no player to decline or confirm'


class OnlyCreatorMayConfirmOrDecline(APIException):
    status_code = 400
    default_detail = 'Only the Match Creator may confirm or decline the ' \
                     'matchup'


class AlreadyJoined(APIException):
    status_code = 400
    default_detail = "You already joined this match!"


class AlreadyConfirmed(APIException):
    status_code = 400
    default_detail = "This match has already been confirmed. You CAN'T" \
                     "leave this match without cancelling."


class NotInMatch(APIException):
    status_code = 400
    default_detail = "You are not in this match"


class CourtAlreadyExists(APIException):
    status_code = 400
    default_detail = "This Court Already Exists."


class UserAlreadyExists(APIException):
    status_code = 400
    default_detail = "That username is taken. Please try again."


class NonExistingPlayer(APIException):
    status_code = 400
    default_detail = "The player you are trying to rate does not exist."
