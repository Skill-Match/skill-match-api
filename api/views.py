import json
from api.exceptions import OneFeedbackAllowed, TwoPlayersPerMatch, SelfSignUp, \
    OnlyCreatorMayConfirmOrDecline, NoPlayerToConfirmOrDecline, AlreadyJoined, \
    AlreadyConfirmed, NotInMatch
from api.serializers import UserSerializer, ParkSerializer, MatchSerializer,\
    FeedbackSerializer, ChallengerMatchSerializer, CreateParkSerializer, \
    ProfileSerializer, CourtSerializer
from django.contrib.auth.models import User
from django.shortcuts import render
from matchup.models import Park, Match, Feedback, Court
from api.notifications import join_match_notify, confirm_match_notify, \
    decline_match_notify, leave_match_notify, challenge_declined_notify, \
    challenge_accepted_notify
import oauth2
import requests
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from skill_match.settings import CONSUMER_KEY, CONSUMER_SECRET, TOKEN, \
    TOKEN_SECRET
from users.models import Profile
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        username = token.user.username
        user_id = token.user.id
        return Response({'token': token.key, 'username':username,
                         'user_id': user_id})


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
        players = [user,]
        serializer.save(creator=user, players=players)


    def get_queryset(self):
        """Return list for user only"""
        qs = super().get_queryset()
        username = self.request.query_params.get('username', None)
        if username:
            qs = qs.filter(players__username=username)
        return qs


class ChallengeCreateMatch(generics.CreateAPIView):
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        user = self.request.user
        challenge_id = serializer.initial_data['challenge']
        challenged = User.objects.get(pk=challenge_id)
        players = [user, challenged]
        serializer.save(creator=user, players=players, is_open=False,
                        is_challenge=True)

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


class JoinMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        joiner = self.request.user
        creator = serializer.instance.creator

        if joiner == creator:
            raise SelfSignUp

        sport = serializer.instance.sport
        players = serializer.instance.players.all()
        player_list = list(players)

        if joiner in player_list:
            raise AlreadyJoined

        player_list.append(joiner)

        if sport == 'Tennis':
            match = serializer.save(players=player_list, is_open=False)
            join_match_notify(match, joiner)
        else:
            serializer.save(players=player_list)


class LeaveMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer
    
    def perform_update(self, serializer):
        if serializer.instance.is_confirmed:
            raise AlreadyConfirmed

        leaver = self.request.user
        sport = serializer.instance.sport
        players = serializer.instance.players.all()
        player_list = list(players)

        if leaver not in player_list:
            raise NotInMatch
        else:
            player_list.remove(leaver)

            if sport == 'Tennis':
                match = serializer.save(players=player_list, is_open=True)
                leave_match_notify(match, leaver)
            else:
                serializer.save(players=player_list)


class DeclineMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        if serializer.instance.players.count() == 1:
            raise NoPlayerToConfirmOrDecline

        decliner = self.request.user
        challenger = serializer.instance.players.exclude(id=decliner.id)[0]

        if serializer.instance.is_challenge == True:
            if challenger == serializer.instance.creator:
                match = serializer.save(challenge_declined=True)
                challenge_declined_notify(match, challenger)
        else:
            if not decliner == serializer.instance.creator:
                raise OnlyCreatorMayConfirmOrDecline

            match = serializer.save(players=[decliner,], is_open=True)
            decline_match_notify(match, challenger)


class ConfirmMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        if serializer.instance.players.count() == 1:
            raise NoPlayerToConfirmOrDecline

        confirmer = self.request.user
        
        if serializer.instance.is_challenge:
            match = serializer.save(is_confirmed=True)
            challenge_accepted_notify(match)
        else:
            if not confirmer == serializer.instance.creator:
                raise OnlyCreatorMayConfirmOrDecline

            match = serializer.save(is_confirmed=True)
            confirm_match_notify(match)


class ListCreateCourts(generics.ListCreateAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer


@api_view(['GET'])
def get_credentials(request):
    if request.method == 'GET':
        key = request.auth.key
        token = Token.objects.get(key=key)
        username = token.user.username
        id = token.user.id

        return Response({"username": username, "user_id": id})


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
