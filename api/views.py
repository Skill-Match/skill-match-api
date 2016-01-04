import json

import cloudinary
import cloudinary.uploader
import cloudinary.api
from api.exceptions import OneFeedbackAllowed, TwoPlayersPerMatch, SelfSignUp, \
    OnlyCreatorMayConfirmOrDecline, NoPlayerToConfirmOrDecline, AlreadyJoined, \
    AlreadyConfirmed, NotInMatch, CourtAlreadyExists, UserAlreadyExists, \
    NonExistingPlayer
from api.serializers import UserSerializer, ParkSerializer, MatchSerializer,\
    FeedbackSerializer, ChallengerMatchSerializer, \
    ProfileSerializer, CourtSerializer, ListParksSerializer
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
import logging
logger = logging.getLogger(__name__)



class ObtainAuthToken(APIView):
    """
    Overwrite built in function to return username and user_id with token
    """
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
        profile.save()
        serializer.save()


class DetailUpdateProfile(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ListParks(generics.ListAPIView):
    """Permissions: all"""
    queryset = Park.objects.all()
    serializer_class = ListParksSerializer
    pagination_class = SmallPagination

    def get_queryset(self):
        """
        Querysets:
        USER LOCATION
        ZIP CODE

        :return: Parks ordered by distance how far from user or zip code
        """
        qs = super().get_queryset()
        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('long', None)
        zip_code = self.request.query_params.get('zip', None)

        if latitude and longitude:
            pnt = G('POINT(' + str(longitude) + ' ' + str(latitude) + ')', srid=4326)
        elif zip_code:
            geolocator = Nominatim()
            location = geolocator.geocode(zip_code + ' NV')
            pnt = G('POINT(' + str(location.longitude) + ' ' + str(location.latitude) + ')', srid=4326)
            x = 5
        else:
            pnt = G('POINT(-115.13983 36.169941)', srid=4326)

        by_distance = qs.annotate(distance=Distance('location', pnt)).order_by('distance')[:20]
        return by_distance


class ListCreateMatches(generics.ListCreateAPIView):
    """Permissions: logged in user or admin"""
    queryset = Match.objects.all().order_by('-created_at')
    serializer_class = MatchSerializer
    pagination_class = SmallPagination

    def perform_create(self, serializer):
        """
        Add creator to serializer, add img_url to serializer based on sport.
        :param serializer:
        :return:
        """
        user = self.request.user
        x = serializer.initial_data['fudge']
        sport = serializer.initial_data['sport']

        if sport == 'Tennis':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803727/1451824644_tennis_jegpea.png"
        elif sport == 'Basketball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451811954/basketball_lxzgmw.png"
        elif sport == 'Football':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451812093/American-Football_vbp5ww.png"
        elif sport == 'Soccer':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803724/1451824570_soccer_mwvtwy.png"
        elif sport == 'Volleyball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803790/1451824851_volleyball_v2pu0m.png"
        elif sport == 'Pickleball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803795/1451824990_table_tennis_uqv436.png"
        else:
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451804013/trophy_200_cnaras.jpg"

        serializer.save(creator=user, img_url=img_url)

    def get_queryset(self):
        """Querysets:
        LOCATION
        SPORT
        USERNAME
        HOME - lose this
        LATITUDE & LONGITUDE
        ZIP CODE

        If no location provided, it will default to Las Vegas, NV
        """
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
            location = geolocator.geocode(zip_code + ' NV')
            pnt = G('POINT(' + str(location.longitude) + ' ' + str(location.latitude) + ')', srid=4326)
        else:
            pnt = G('POINT(-115.13983 36.169941)', srid=4326)

        by_distance = qs.annotate(distance=Distance('park__location', pnt)).order_by('distance')[:30]
        return by_distance


class ChallengeCreateMatch(generics.CreateAPIView):
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        """
        Adds player making request and finds challenged(User) by id. Adds both
        players into list to serializer. Adds img_url based on sport, closes sport
        and indicates it's a challenge with is_challenge=True
        :param serializer:
        :return:
        """
        user = self.request.user
        challenge_id = serializer.initial_data['challenge']
        challenged = User.objects.get(pk=challenge_id)
        if challenged == user:
            raise SelfSignUp
        players = [user, challenged]
        sport = serializer.initial_data['sport']

        if sport == 'Tennis':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803727/1451824644_tennis_jegpea.png"
        elif sport == 'Basketball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451811954/basketball_lxzgmw.png"
        elif sport == 'Football':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451812093/American-Football_vbp5ww.png"
        elif sport == 'Soccer':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803724/1451824570_soccer_mwvtwy.png"
        elif sport == 'Volleyball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803790/1451824851_volleyball_v2pu0m.png"
        elif sport == 'Pickleball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803795/1451824990_table_tennis_uqv436.png"
        else:
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451804013/trophy_200_cnaras.jpg"

        serializer.save(creator=user, players=players, is_open=False,
                        is_challenge=True, img_url=img_url)


class CreateFeedbacks(generics.CreateAPIView):
    """Logged in user only, *** must be player in the match also ***"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
        """If no player, Get match_id from serializer. Find Match object with match_id. Use Match
            object to find player and reviewer from the match. (Reviewer =
            logged in user.
          If player, use player_id to find User to be reviewed
          Error if they already provided Feedback for that player.
        """
        reviewer = self.request.user
        match_id = serializer.initial_data['match']
        match = Match.objects.get(pk=match_id)
        player_id = serializer.initial_data.get('player', None)
        if player_id:

            # if id for player does not match a user , error
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
    """Permissions: detail-all, update/destroy - match creator only"""
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class JoinMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        """
        Gets all players from serializer and puts them in player_list. Add the
        User making the request to the player_list.
        If Sport is Tennis, close match and notify match creator using
        join_match_notify() from notifications.
        :param serializer:
        :return:
        """
        joiner = self.request.user
        creator = serializer.instance.creator
        if joiner == creator:
            raise SelfSignUp

        players = serializer.instance.players.all()
        player_list = list(players)

        if joiner in player_list:
            raise AlreadyJoined

        player_list.append(joiner)
        sport = serializer.instance.sport

        if sport == 'Tennis':
            match = serializer.save(players=player_list, is_open=False)
            join_match_notify(match, joiner)
        else:
            serializer.save(players=player_list)


class LeaveMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer
    
    def perform_update(self, serializer):
        """
        Users may leave a match if they get tired waiting for Match creator to
        confirm.
        If requesting user is in match, and the match is not confirmed already,
        they are removed from player_list.
        If sport is Tennis, match opens up again.
        Match creator is notified that the user left match and match is
        open again.
        :param serializer:
        :return:
        """
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
        """
        Remove User (challenger) from Match. Notify match challenger.
        Match is opened again if not a challenge.

        :param serializer:
        :return:
        """
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
        """
        Confirm match. Only change here is is_confirmed=True. Needs refactor
        with Match model
        :param serializer:
        :return:
        """
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
        """
        Check to see if the Sport already exists on the park.
        If latitude and longitude are provided, pass them to the serializer.
        :param serializer:
        :return:
        """
        park_id = serializer.initial_data['park']
        sport = serializer.initial_data['sport']
        park = Park.objects.get(pk=park_id)
        if not sport == 'Other':
            already_exists = park.court_set.filter(sport=sport)
            if already_exists:
                raise CourtAlreadyExists

        if sport == 'Tennis':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803727/1451824644_tennis_jegpea.png"
        elif sport == 'Basketball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451811954/basketball_lxzgmw.png"
        elif sport == 'Football':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451812093/American-Football_vbp5ww.png"
        elif sport == 'Soccer':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803724/1451824570_soccer_mwvtwy.png"
        elif sport == 'Volleyball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803790/1451824851_volleyball_v2pu0m.png"
        elif sport == 'Pickleball':
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451803795/1451824990_table_tennis_uqv436.png"
        else:
            img_url = "http://res.cloudinary.com/skill-match/image/upload/v1451804013/trophy_200_cnaras.jpg"

        lat = serializer.initial_data.get('lat', None)
        long = serializer.initial_data.get('long', None)
        if lat and long:
            serializer.save(lat=lat, long=long, img_url=img_url)
        else:
            serializer.save(img_url=img_url)


class DetailUpdateCourt(generics.RetrieveUpdateDestroyAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer


@api_view()
def hello_world(request):
    """
    Not being used in the scope of the project at the moment. It
        fetches data from yelp api and sends it through this project api.
        It finds the top 20 parks in the area code of 89148 from Yelp.
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


def myfunction():
    logger.debug("this is a debug message!")

def myotherfunction():
    logger.error("this is an error message!!")