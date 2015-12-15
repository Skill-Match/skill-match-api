import json
from api.exceptions import OneFeedbackAllowed, TwoPlayersPerMatch, SelfSignUp, \
    OnlyCreatorMayConfirmOrDecline, NoPlayerToConfirmOrDecline
from api.serializers import UserSerializer, ParkSerializer, MatchSerializer,\
    FeedbackSerializer, ChallengerMatchSerializer, CreateParkSerializer
from django.contrib.auth.models import User
from django.shortcuts import render
from matchup.models import Park, Match, Feedback
import oauth2
import requests
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from skill_match.settings import CONSUMER_KEY, CONSUMER_SECRET, TOKEN, \
    TOKEN_SECRET


class SmallPagination(PageNumberPagination):
    page_size = 10


class ListUsers(generics.ListAPIView):
    """
    Permissions:
        ONLY ADMIN or show-users?
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (permissions.IsAdminUser, )


class CreateUser(generics.CreateAPIView):
    """Permissions: any"""
    serializer_class = UserSerializer


class DetailUpdateUser(generics.RetrieveUpdateDestroyAPIView):
    """Permissions: User only or ADMIN"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ListParks(generics.ListAPIView):
    """Permissions: all"""
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


class CreatePark(generics.CreateAPIView):
    """Permissions: logged in user only"""
    serializer_class = CreateParkSerializer


class ListCreateMatches(generics.ListCreateAPIView):
    """Permissions: logged in user for create"""
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    pagination_class = SmallPagination

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(creator=user)

    def get_queryset(self):
        """Return list for user only"""
        qs = super().get_queryset()
        username = self.request.query_params.get('username', None)
        if username:
            qs = qs.filter(players__username=username)
        return qs


class ListFeedbacks(generics.ListAPIView):
    """Permissions: ADMIN only"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class CreateFeedbacks(generics.CreateAPIView):
    """Logged in user only, *** must be player in the match also ***"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
        """Grab match_id from form. Find Match object with match_id. Use Match
            object to find player and reviewer from the match. (Reviewer =
            logged in user.
        """
        reviewer = self.request.user
        match_id = serializer.initial_data['match']
        match = Match.objects.get(pk=match_id)
        existing_feedback = match.feedback_set.filter(reviewer=reviewer)
        if existing_feedback:
            raise OneFeedbackAllowed
        for person in match.players.all():
            if not person == reviewer:
                player = person
        serializer.save(player=player, reviewer=reviewer)


class DetailUpdateFeedback(generics.RetrieveUpdateDestroyAPIView):
    """
    Permissions: ADMIN or user only.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class DetailPark(generics.RetrieveAPIView):
    """ Permissions: all
    """
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


class DetailUpdateMatch(generics.RetrieveUpdateDestroyAPIView):
    """Permissions: all, for update--match creator only"""
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class UpdateMatch(generics.UpdateAPIView):
    """Permissions:  """
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        """find query parameters.
            'decline' or 'confirm' match
            **if no query parameter, this endpoint will sign up the
                requested user**
        """
        decline = self.request.query_params.get('decline', None)
        confirm = self.request.query_params.get('confirm', None)
        requester = self.request.user
        if decline:
            serializer.save(decline=decline, is_open=True, requester=requester,)
        elif confirm:
            serializer.save(confirm=confirm, requester=requester)
        else:
            serializer.save(challenger=requester)


class JoinMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        challenger=self.request.user
        creator = serializer.instance.creator
        player_count = serializer.instance.players.count()
        if player_count > 1:
             raise TwoPlayersPerMatch
        if challenger == creator:
            raise SelfSignUp

        players = [creator, challenger]
        serializer.save(players=players, is_open=False)

class DeclineMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        decliner = self.request.user
        if not decliner == serializer.instance.creator:
            raise OnlyCreatorMayConfirmOrDecline
        if serializer.instance.players.count() == 1:
            raise NoPlayerToConfirmOrDecline

        serializer.save(players=[decliner,], is_open=True)


class ConfirmMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        confirmer = self.request.user
        if not confirmer == serializer.instance.creator:
            raise OnlyCreatorMayConfirmOrDecline
        if serializer.instance.players.count() == 1:
            raise NoPlayerToConfirmOrDecline

        serializer.save(is_confirmed=True)


@api_view()
def hello_world(request):
    """
    Not being used in the scope of the project at the moment. But it works. It
        fetches data from yelp api and sends it through this project api.
    :param request:
    :return:
    """
    url = 'http://api.yelp.com/v2/search/' + '?location=89148, NV &category_filter=parks'

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    response = requests.get(signed_url)
    content = response.json()
    parks = content['businesses']
    a = parks[0]['id']
    name = parks[0]['name']
    data = {"message": "hello"}
    return Response(content)