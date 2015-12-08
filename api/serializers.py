from django.contrib.auth.models import User
from matchup.models import Park, Match, Feedback
from rest_framework import serializers
from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """One to One with User
    """
    class Meta:
        model = Profile
        exclude = ('user',)


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
        fields = ('id', 'name',)
        read_only_fields = ('id',)

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'park', 'players')
        read_only_fields = ('id',)

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('__all__')
        read_only_fields = ('id')