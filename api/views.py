import json
from api.exceptions import OneFeedbackAllowed
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (permissions.IsAdminUser, )


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer


class DetailUpdateUser(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ListParks(generics.ListAPIView):
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


class CreatePark(generics.CreateAPIView):
    serializer_class = CreateParkSerializer


class ListCreateMatches(generics.ListCreateAPIView):
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
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class CreateFeedbacks(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
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


class DetailFeedback(generics.RetrieveAPIView):
    queryset = Match.objects.all()
    serializer_class = FeedbackSerializer


class DetailPark(generics.RetrieveAPIView):
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


class DetailUpdateMatch(generics.RetrieveUpdateDestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class UpdateMatch(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        decline = self.request.query_params.get('decline', None)
        confirm = self.request.query_params.get('confirm', None)
        requester = self.request.user
        if decline:
            serializer.save(decline=decline, requester=requester)
        elif confirm:
            serializer.save(confirm=confirm, requester=requester)
        else:
            serializer.save(challenger=requester)


@api_view()
def hello_world(request):
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