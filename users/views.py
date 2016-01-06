from django.contrib.auth.models import User
from django.shortcuts import render
from matchup.serializers import UserSerializer
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics


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