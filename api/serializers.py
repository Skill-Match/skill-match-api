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

    profile = ProfileSerializer(read_only=True)
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
            age=profile_data.get('age'),
            phone_number=profile_data.get('phone_number'),
            wants_texts=profile_data.get('wants_texts')
        )
        return user


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('pic_url',)


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
    # players = serializers.StringRelatedField(many=True, read_only=True)
    players = UserSerializer(many=True, read_only=True)
    date = serializers.DateField(format="%A %b, %d")
    distance = serializers.DecimalField(source='distance.mi', max_digits=10, decimal_places=2, required=False, read_only=True)

    class Meta:
        model = Match
        fields = ('id', 'creator', 'creator_name', 'description', 'park',
                  'park_name', 'sport', 'other', 'skill_level', 'date', 'time',
                  'players', 'img_url', 'is_open', 'is_completed',
                  'is_confirmed', 'is_challenge', 'challenge_declined',
                  'is_succesful', 'distance')

        read_only_fields = ('id', 'creator', 'players', 'is_open',
                            'is_completed', 'is_confirmed', 'img_url',
                            'is_challenge', 'challenge_declined',
                            'is_succesful')

    def create(self, validated_data):
        x = super().create(validated_data)
        creator = validated_data['creator']

        x.players.add(creator)
        x.save()
        return x


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

class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ('id', 'park', 'sport', 'other', 'num_courts')


class ParkSerializer(serializers.ModelSerializer):
    match_set = MatchSerializer(many=True, read_only=True)
    court_set = CourtSerializer(many=True, read_only=True)
    distance = serializers.DecimalField(source='distance.mi', max_digits=10, decimal_places=2)

    class Meta:
        model = Park
        fields = ('id', 'name', 'rating', 'url', 'image_url', 'city', 'state_code',
                  'display_address1', 'display_address2', 'display_address3',
                  'postal_code', 'match_set', 'court_set', 'distance')
        read_only_fields = ('id', 'name', 'rating', 'url', 'image_url', 'city', 'state_code',
                            'display_address1', 'display_address2',
                            'display_address3', 'postal_code')


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'reviewer', 'player', 'match', 'skill',
                  'sportsmanship', 'punctuality', 'availability')
        read_only_fields = ('id', 'reviewer', 'player',)
