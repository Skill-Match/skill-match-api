from django.contrib.auth.models import User
from matchup.models import Park, Match, Feedback, Skill, Court
from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from users.models import Profile


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ('sport', 'skill', 'num_feedbacks')
        read_only_fields = ('sport', 'skill', 'num_feedbacks')



class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('gender', 'age', 'phone_number', 'wants_texts',
                  'pic_url', 'sportsmanship')
        read_only_fields = ('pic_url', 'sportsmanship')


class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()

    skill_set = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile', 'skill_set')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create Profile for User when registered

        """
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


class CreateParkSerializer(serializers.ModelSerializer):
    """
        Extra Park Serializer for creation. This is so only logged in users can
        create park objects. Is this necessary?
    """
    class Meta:
        model = Park
        fields = ('id', 'name', 'city', 'postal_code', 'display_address1',
                  'display_address2', 'display_address3' )
        read_only_fields = ('id',)


class MatchSerializer(serializers.ModelSerializer):
    park_name = serializers.ReadOnlyField(source='park.name')
    creator_name = serializers.ReadOnlyField(source='creator.username')
    time = serializers.TimeField(format="%I:%M %p")

    class Meta:
        model = Match
        fields = ('id', 'creator', 'creator_name', 'description', 'park', 'park_name', 'sport',
                  'other', 'skill_level', 'date', 'time', 'players',
                  'is_open', 'is_completed', 'is_confirmed')
        read_only_fields = ('id', 'creator', 'players', 'is_open',
                            'is_completed', 'is_confirmed')


class ChallengerMatchSerializer(serializers.ModelSerializer):
    """
        Separate Serializer for Updating Match.
    """
    class Meta:
        model = Match
        fields = ('id', 'creator', 'description', 'park', 'sport',
                  'skill_level', 'date', 'time', 'players',
                  'is_open', 'is_completed', 'is_confirmed')
        read_only_fields = ('id', 'creator', 'description', 'park', 'sport',
                            'skill_level', 'date', 'time', 'players',
                            'is_open', 'is_completed', 'is_confirmed')


class ParkSerializer(serializers.ModelSerializer):
    match_set = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = Park
        fields = ('id', 'name', 'rating', 'url', 'city', 'state_code',
                  'display_address1', 'display_address2', 'display_address3',
                  'postal_code', 'match_set')
        read_only_fields = ('id', 'name', 'rating', 'url', 'city', 'state_code',
                            'display_address1', 'display_address2',
                            'display_address3', 'postal_code')


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'reviewer', 'player', 'match', 'skill',
                  'sportsmanship', 'punctuality', 'availability')
        read_only_fields = ('id', 'reviewer', 'player',)


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ('id', 'park', 'num_courts')


