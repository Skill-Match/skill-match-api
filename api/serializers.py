from api.exceptions import OneFeedbackAllowed, TwoPlayersPerMatch, SelfSignUp, \
    NoPlayerToConfirmOrDecline, OnlyCreatorMayConfirmOrDecline
from django.contrib.auth.models import User
from matchup.models import Park, Match, Feedback
from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """One to One with User
    """
    class Meta:
        model = Profile
        fields = ('gender', 'age', 'skill', 'sportsmanship')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id', )

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        profile_data = validated_data.pop('profile')
        profile = Profile.objects.create(
            user=user,
            gender=profile_data.get('gender'),
            age=profile_data.get('age')
        )
        return user


class ParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Park
        fields = ('id', 'name', 'rating', 'url', 'city', 'state_code',
                  'display_address1', 'display_address2', 'display_address3',
                  'postal_code')
        read_only_fields = ('id', 'name', 'rating', 'url', 'city', 'state_code',
                            'display_address1', 'display_address2',
                            'display_address3', 'postal_code')


class MatchSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()

    def get_creator_name(self, obj):
      return obj.creator.username

    class Meta:
        model = Match
        fields = ('id', 'creator', 'creator_name', 'description', 'park', 'sport',
                  'skill_level', 'date', 'time', 'players',
                  'is_open', 'is_completed', 'is_confirmed')
        read_only_fields = ('id', 'creator', 'players', 'is_open',
                            'is_completed', 'is_confirmed')

    def create(self, validated_data):
        match = super().create(validated_data)
        creator = validated_data['creator']
        match.players.add(creator)
        match.save()
        return match

    # def update(self, instance, validated_data):
    #     match = super().update(instance, validated_data)
    #     decline = validated_data.get('decline', None)
    #     if decline:
    #         creator_username = match.creator.username
    #         challenger = match.players.exclude(username=creator_username)[0]
    #         match.players.remove(challenger)
    #         match.is_open = True
    #         match.save()
    #
    #     return match


class ChallengerMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'creator', 'description', 'park', 'sport',
                  'skill_level', 'date', 'time', 'players',
                  'is_open', 'is_completed', 'is_confirmed')
        read_only_fields = ('id', 'creator', 'description', 'park', 'sport',
                            'skill_level', 'date', 'time', 'players',
                            'is_open', 'is_completed', 'is_confirmed')

    def update(self, instance, validated_data):
        match = super().update(instance, validated_data)
        requester = validated_data.get('requester', None)
        decline = validated_data.get('decline', None)
        confirm = validated_data.get('confirm', None)
        challenger = validated_data.get('challenger', None)
        if challenger:
            if match.players.count() == 2:
                raise TwoPlayersPerMatch
            if challenger == match.creator:
                raise SelfSignUp
            match.players.add(challenger)
            match.is_open = False
            match.save()

        elif confirm:
            if not requester == match.creator:
                raise OnlyCreatorMayConfirmOrDecline
            if match.players.count() == 1:
                raise NoPlayerToConfirmOrDecline
            match.is_confirmed = True
            match.save()

        elif decline:
            if not requester == match.creator:
                raise OnlyCreatorMayConfirmOrDecline
            if match.players.count() == 1:
                raise NoPlayerToConfirmOrDecline
            creator_username = match.creator.username
            challenger = match.players.exclude(username=creator_username)[0]
            match.players.remove(challenger)
            match.is_open = True
            match.save()

        return match


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'reviewer', 'player', 'match', 'skill',
                  'sportsmanship', 'punctuality', 'availability')
        read_only_fields = ('id', 'reviewer', 'player',)