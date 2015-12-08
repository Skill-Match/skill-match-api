from api.serializers import UserSerializer, ParkSerializer, MatchSerializer, \
    FeedbackSerializer
from django.contrib.auth.models import User
from django.shortcuts import render
from matchup.models import Park, Match, Feedback
from rest_framework import generics


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
        serializer.save(user=user)


class ListFeedbacks(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class CreateFeedbacks(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class DetailFeedback(generics.RetrieveAPIView):
    queryset = Match.objects.all()
    serializer_class = FeedbackSerializer


class DetailPark(generics.RetrieveAPIView):
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


class DetailUpdateMatch(generics.RetrieveUpdateDestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

