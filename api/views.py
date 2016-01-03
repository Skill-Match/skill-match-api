import json

import cloudinary
import cloudinary.uploader
import cloudinary.api
from api.exceptions import OneFeedbackAllowed, TwoPlayersPerMatch, SelfSignUp, \
    OnlyCreatorMayConfirmOrDecline, NoPlayerToConfirmOrDecline, AlreadyJoined, \
    AlreadyConfirmed, NotInMatch, CourtAlreadyExists, UserAlreadyExists, \
    NonExistingPlayer
from api.serializers import UserSerializer, ParkSerializer, MatchSerializer,\
    FeedbackSerializer, ChallengerMatchSerializer, CreateParkSerializer, \
    ProfileSerializer, CourtSerializer
from django.contrib.auth.models import User
from django.shortcuts import render
from geopy import Nominatim
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
from django.contrib.gis.geos import GEOSGeometry as G
from django.contrib.gis.db.models.functions import Distance


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

    def perform_create(self, serializer):
        if self.request.FILES:
            image = cloudinary.uploader.upload(self.request.FILES['profile.avatar'])
            image_url = image['url']
            serializer.save(image_url=image_url)
        else:
            serializer.save()

class DetailUpdateUser(generics.RetrieveUpdateDestroyAPIView):
    """Permissions: User only or ADMIN"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_update(self, serializer):
        user = serializer.instance
        username = serializer.initial_data['username']
        age = serializer.initial_data['profile.age']
        gender = serializer.initial_data['profile.gender']
        phone = serializer.initial_data['profile.phone_number']
        texts = serializer.initial_data.get('profile.wants_texts', None)
        profile = Profile.objects.get(user=user)
        if texts:
            profile.wants_texts = texts
        profile.age = age
        profile.gender = gender
        profile.phone_number = phone
        if self.request.FILES:
            image = cloudinary.uploader.upload(self.request.FILES['profile.avatar'])
            image_url = image['url']
            profile.pic_url = image_url
        profile.save()
        serializer.save()


class ListParks(generics.ListAPIView):
    """Permissions: all"""
    queryset = Park.objects.all()
    serializer_class = ParkSerializer
    pagination_class = SmallPagination

    def get_queryset(self):
        qs = super().get_queryset()
        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('long', None)
        zip_code = self.request.query_params.get('zip', None)

        if latitude and longitude:
            pnt = G('POINT(' + str(longitude) + ' ' + str(latitude) + ')', srid=4326)
        elif zip_code:
            geolocator = Nominatim()
            location = geolocator.geocode(zip_code)
            pnt = G('POINT(' + str(location.longitude) + ' ' + str(location.latitude) + ')', srid=4326)
        else:
            pnt = G('POINT(-115.13983 36.169941)', srid=4326)

        by_distance = qs.annotate(distance=Distance('location', pnt)).order_by('distance')[:20]
        return by_distance

class CreatePark(generics.CreateAPIView):
    """Permissions: logged in user only"""
    serializer_class = CreateParkSerializer


class ListCreateMatches(generics.ListCreateAPIView):
    """Permissions: logged in user for create"""
    queryset = Match.objects.all().order_by('-created_at')
    serializer_class = MatchSerializer
    pagination_class = SmallPagination

    def perform_create(self, serializer):
        user = self.request.user
        sport = serializer.initial_data['sport']

        if sport == 'Tennis':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733cc2dc5cb4b9e2e1b062/1450392771257/?format=500w"
        elif sport == 'Basketball':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733c47e0327c81fa9a2a1f/1450392648388/?format=500w"
        elif sport == 'Football':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733bf8e0327c81fa9a2787/1450392569419/?format=500w"
        elif sport == 'Soccer':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733cb3dc5cb4b9e2e1afce/1450392756140/?format=500w"
        else:
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733e05a128e6b1e54ff616/1450393093587/?format=500w"

        serializer.save(creator=user, img_url=img_url)

    def get_queryset(self):
        """Return Pledges for user only"""
        qs = super().get_queryset()
        sport = self.request.query_params.get('sport', None)
        home = self.request.query_params.get('home', None)
        username = self.request.query_params.get('username', None)
        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('long', None)
        zip_code = self.request.query_params.get('zip', None)
        if sport:
            sport = sport.title()
            qs = qs.filter(sport=sport)
        if username:
            qs = qs.filter(players__username=username).order_by('-date')
        if home:
            qs = qs.filter(is_open=True).order_by('date')
        if latitude and longitude:
            pnt = G('POINT(' + str(longitude) + ' ' + str(latitude) + ')', srid=4326)
        elif zip_code:
            geolocator = Nominatim()
            location = geolocator.geocode(zip_code)
            pnt = G('POINT(' + str(location.longitude) + ' ' + str(location.latitude) + ')', srid=4326)
        else:
            pnt = G('POINT(-115.13983 36.169941)', srid=4326)

        by_distance = qs.annotate(distance=Distance('park__location', pnt)).order_by('distance')[:20]
        return by_distance


class ChallengeCreateMatch(generics.CreateAPIView):
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        user = self.request.user
        challenge_id = serializer.initial_data['challenge']
        challenged = User.objects.get(pk=challenge_id)
        if challenged == user:
            raise SelfSignUp
        players = [user, challenged]
        sport = serializer.initial_data['sport']

        if sport == 'Tennis':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733cc2dc5cb4b9e2e1b062/1450392771257/?format=500w"
        elif sport == 'Basketball':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733c47e0327c81fa9a2a1f/1450392648388/?format=500w"
        elif sport == 'Football':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733bf8e0327c81fa9a2787/1450392569419/?format=500w"
        elif sport == 'Soccer':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733cb3dc5cb4b9e2e1afce/1450392756140/?format=500w"
        elif sport == 'Other':
            img_url = "http://static1.squarespace.com/static/54484b66e4b084696e53f369/t/56733e05a128e6b1e54ff616/1450393093587/?format=500w"

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
        player_id = serializer.initial_data.get('player', None)
        if player_id:

            # this error is for Front End team
            existing_user = User.objects.filter(id=player_id)
            if not existing_user:
                raise NonExistingPlayer

            player = User.objects.get(pk=player_id)
            existing_feedback = match.feedback_set.filter(reviewer=reviewer, player=player)
            if existing_feedback:
                raise OneFeedbackAllowed
            serializer.save(player=player, reviewer=reviewer)
        else:
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
        if leaver == serializer.instance.creator:
            raise SelfSignUp

        sport = serializer.instance.sport
        players = serializer.instance.players.all()
        player_list = list(players)

        if leaver not in player_list:
            raise NotInMatch

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

    def perform_create(self, serializer):
        park_id = serializer.initial_data['park']
        sport = serializer.initial_data['sport']
        park = Park.objects.get(pk=park_id)
        already_exists = park.court_set.filter(sport=sport)
        if already_exists:
            raise CourtAlreadyExists

        serializer.save()

class DetailUpdateCourt(generics.RetrieveUpdateDestroyAPIView):
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
