from api.exceptions import OneFeedbackAllowed
from api.serializers import UserSerializer, ParkSerializer, MatchSerializer, \
    FeedbackSerializer
from django.contrib.auth.models import User
from django.shortcuts import render
from matchup.models import Park, Match, Feedback
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied


class ListUsers(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (permissions.IsAdminUser, )


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer


class ListCreateParks(generics.ListCreateAPIView):
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


class ListCreateMatches(generics.ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(creator=user)


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