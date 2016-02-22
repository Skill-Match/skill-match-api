import logging
import oauth2
import re
import requests
from django.contrib.auth.models import User
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry as Geos
from django.db.models import Count
from geopy import Nominatim
from matchup.exceptions import OneFeedbackAllowed, SelfSignUp, \
    OnlyCreatorMayConfirmOrDecline, NoPlayerToConfirmOrDecline, \
    AlreadyJoined, AlreadyConfirmed, NotInMatch, CourtAlreadyExists, \
    NonExistingPlayer
from matchup.models import Park, Match, Feedback, Court
from matchup.notifications import join_match_notify, confirm_match_notify, \
    decline_match_notify, leave_match_notify, challenge_declined_notify, \
    challenge_accepted_notify, create_match_notify
from matchup.permissions import IsOwnerOrReadOnly, IsOwner
from matchup.serializers import ParkSerializer, \
    MatchSerializer, FeedbackSerializer, ChallengerMatchSerializer, \
    CourtSerializer, ListParksSerializer
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from skill_match.settings import YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET, \
    YELP_TOKEN, YELP_TOKEN_SECRET

logger = logging.getLogger(__name__)

###############################################################################
#
# Image URL's used for sport representation
#
###############################################################################

TENNIS_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803727/1451824644_tennis_jegpea.png"
BASKETBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451811954/basketball_lxzgmw.png"
FOOTBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                   "c_scale,w_200/v1451812093/American-Football_vbp5ww.png"
SOCCER_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803724/1451824570_soccer_mwvtwy.png"
VOLLEYBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803790/1451824851_" \
                     "volleyball_v2pu0m.png"
PICKLEBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803795/1451824990_" \
                     "table_tennis_uqv436.png"
TROPHY_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                "v1451804013/trophy_200_cnaras.jpg"


class SmallPagination(PageNumberPagination):
    page_size = 10


###############################################################################
#
# PARK Related Views
#
###############################################################################


class ListParks(generics.ListAPIView):
    """
    Permissions: All
    """
    queryset = Park.objects.all()
    serializer_class = ListParksSerializer
    pagination_class = SmallPagination

    def get_queryset(self):
        """
        Querysets:
        1. lat and long (latitude and longitude): use to order by distance
        2. search: if 5-digit *zip code, use for distance, otherwise search for
                   park name
        3. sport: only include parks with that sport
        4. courts: exclude parks with no listed courts

        * Uses Nominatim from the geopy library to get latitude and longitude
        based on the zipcode.

        Default Ordering: by distance
        If no location provided, default location is Las Vegas, NV.
        Uses Geos Point objects to order by distance.

        :return: Parks ordered by distance
        """
        qs = super().get_queryset()
        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('long', None)
        search = self.request.query_params.get('search', None)
        sport = self.request.query_params.get('sport', None)
        courts = self.request.query_params.get('courts', None)
        pnt = None

        if sport:
            sport = sport.title()
            qs = qs.filter(court__sport=sport)
        if courts:
            qs = qs.annotate(count=Count('court')).exclude(count=0)
        if search:
            zip_code = re.match('^\d{5}$', search)
            if zip_code:
                geolocator = Nominatim()
                location = geolocator.geocode(search + ' NV')
                pnt = Geos('POINT(' + str(location.longitude) + ' ' +
                           str(location.latitude) + ')', srid=4326)
            else:
                qs = qs.filter(name__icontains=search)
        if latitude and longitude:
            pnt = Geos('POINT(' + str(longitude) + ' ' + str(latitude) + ')',
                       srid=4326)
        if not pnt:
            pnt = Geos('POINT(-115.13983 36.169941)', srid=4326)

        by_distance = qs.annotate(distance=Distance(
                'location', pnt)).order_by('distance')[:20]
        return by_distance


class DetailPark(generics.RetrieveAPIView):
    # Detail View for Park Detail Page. Thanks for making this easy Django
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


###############################################################################
#
# MATCH Related Views
#
###############################################################################


class ListCreateMatches(generics.ListCreateAPIView):
    """
    Permissions: All may read. Only logged in Users can perform actions.

    Default QuerySet: All Matches ordered by the time they were created,
        although this is overridden in get_queryset to order by distance.
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Match.objects.all().order_by('-created_at')
    serializer_class = MatchSerializer
    pagination_class = SmallPagination

    def perform_create(self, serializer):
        """
        1. Pass logged in user to Match serializer to fill Match creator field.
        2. Add image_url based on sport selected.
        3. Check to see if that park has a court object attached to it with
           the selected sport. If it does not, create a court object for that
           park.
        :param serializer: Initial data submitted by the user.
        :return: NONE
        """
        user = self.request.user
        sport = serializer.initial_data['sport']

        if sport == 'Tennis':
            img_url = TENNIS_IMG_URL
        elif sport == 'Basketball':
            img_url = BASKETBALL_IMG_URL
        elif sport == 'Football':
            img_url = FOOTBALL_IMG_URL
        elif sport == 'Soccer':
            img_url = SOCCER_IMG_URL
        elif sport == 'Volleyball':
            img_url = VOLLEYBALL_IMG_URL
        elif sport == 'Pickleball':
            img_url = PICKLEBALL_IMG_URL
        else:
            img_url = TROPHY_IMG_URL

        match = serializer.save(creator=user, img_url=img_url)
        already_exists = Court.objects.filter(park=match.park,
                                              sport=match.sport)
        if not already_exists:
            Court.objects.create(park=match.park, sport=match.sport)
        create_match_notify(match)

    def get_queryset(self):
        """
        Querysets:
        1. home: filter for only OPEN matches ordered by date of match upcoming
        2. lat and long (latitude and longitude): use to order by distance
        3. *zip code: use to order by distance
        4. sport: only include parks with that sport
        5. username: filter by only matches the user with that username
           participated in

        * Uses Nominatim from the geopy library to get latitude and longitude
        based on the zipcode.

        Default Ordering: by distance
        If no location provided, default location is Las Vegas, NV.
        Uses Geos Point objects to order by distance.

        :return: Matches ordered by distance
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
            qs = qs.filter(sport=sport).filter(is_open=True)
        if username:
            qs = qs.filter(players__username=username).order_by('-date')
        if home:
            qs = qs.filter(is_open=True).order_by('date')
        if latitude and longitude:
            pnt = Geos('POINT(' + str(longitude) + ' ' + str(latitude) + ')',
                    srid=4326)
            qs = qs.filter(is_open=True)
        elif zip_code:
            geolocator = Nominatim()
            location = geolocator.geocode(zip_code + ' NV')
            pnt = Geos('POINT(' + str(location.longitude) + ' ' +
                       str(location.latitude) + ')', srid=4326)
            qs = qs.filter(is_open=True)
        else:
            pnt = Geos('POINT(-115.13983 36.169941)', srid=4326)

        by_distance = qs.annotate(distance=Distance(
                'park__location', pnt)).order_by('distance')
        return by_distance


class ChallengeCreateMatch(generics.CreateAPIView):
    """
    View for the sole purpose of creating a Challenge Match.
    """
    serializer_class = MatchSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        """
        Pass User making request as creator to serializer.
        Find User being challenged (by challenge_id) and pass to serializer.
        Add img_url based on sport.
        Indicate it is a challenge match. (is_challenge=True)
        Close match to public. (is_open=False)

        :param serializer:
        :return: NONE
        """
        user = self.request.user
        challenge_id = serializer.initial_data['challenge']
        challenged = User.objects.get(pk=challenge_id)
        if challenged == user:
            raise SelfSignUp
        sport = serializer.initial_data['sport']

        if sport == 'Tennis':
            img_url = TENNIS_IMG_URL
        elif sport == 'Basketball':
            img_url = BASKETBALL_IMG_URL
        elif sport == 'Football':
            img_url = FOOTBALL_IMG_URL
        elif sport == 'Soccer':
            img_url = SOCCER_IMG_URL
        elif sport == 'Volleyball':
            img_url = VOLLEYBALL_IMG_URL
        elif sport == 'Pickleball':
            img_url = PICKLEBALL_IMG_URL
        else:
            img_url = TROPHY_IMG_URL

        serializer.save(creator=user, challenged=challenged, is_open=False,
                        img_url=img_url, is_challenge=True)


class DetailUpdateMatch(generics.RetrieveUpdateDestroyAPIView):
    # Detail
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


###############################################################################
#
# JOIN, LEAVE, DECLINE, CONFIRM MATCH
#
###############################################################################


class JoinMatch(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
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
    permission_classes = (permissions.IsAuthenticated,)
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
    permission_classes = (permissions.IsAuthenticated,)
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

        if serializer.instance.is_challenge:
            if challenger == serializer.instance.creator:
                match = serializer.save(challenge_declined=True)
                challenge_declined_notify(match, challenger)
        else:
            if not decliner == serializer.instance.creator:
                raise OnlyCreatorMayConfirmOrDecline

            match = serializer.save(players=[decliner,], is_open=True)
            decline_match_notify(match, challenger)


class ConfirmMatch(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
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


###############################################################################
#
# FEEDBACK RELATED VIEWS
#
###############################################################################


class CreateFeedbacks(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
        """If no player, Get match_id from serializer. Find Match object with
           match_id. Use Match object to find player and reviewer from the
           match. (Reviewer = logged in user.
          If player, use player_id to find User to be reviewed
          Error if they already provided Feedback for that player.
        """
        reviewer = self.request.user
        match_id = serializer.initial_data['match']
        match = Match.objects.get(pk=match_id)
        if reviewer not in match.players.all():
            raise NotInMatch
        player_id = serializer.initial_data.get('player', None)
        if player_id:
            # if id for player does not match a user , error
            existing_user = User.objects.filter(id=player_id)
            if not existing_user:
                raise NonExistingPlayer

            player = User.objects.get(pk=player_id)
            existing_feedback = match.feedback_set.filter(reviewer=reviewer,
                                                          player=player)
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
    permission_classes = (IsOwner, )
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

###############################################################################
#
# COURT RELATED VIEWS
#
###############################################################################


class CreateCourts(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
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

        lat = serializer.initial_data.get('lat', None)
        long = serializer.initial_data.get('long', None)
        if lat and long:
            serializer.save(lat=lat, long=long)
        else:
            serializer.save()


class DetailUpdateCourt(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
