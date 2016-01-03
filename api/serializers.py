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
    avatar = serializers.ImageField(required=False)
    class Meta:
        model = Profile
        fields = ('gender', 'age', 'phone_number', 'wants_texts',
                  'pic_url', 'sportsmanship', 'avatar')

        read_only_fields = ('pic_url', 'sportsmanship')


class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()
    skill_set = SkillSerializer(many=True, read_only=True)
    profile_id = serializers.ReadOnlyField(source='profile.id')

    class Meta:
        model = User
        fields = ('id', 'profile_id', 'username', 'email', 'password', 'profile', 'skill_set')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id', 'skill_set')

    def create(self, validated_data):
        """Create Profile for User when registered

        """
        user = User.objects.create_user(
            email=validated_data['email'].lower(),
            username=validated_data['username'].lower(),
            password=validated_data['password']
        )
        profile_data = validated_data.pop('profile')
        profile = Profile.objects.create(
            user=user,
            gender=profile_data.get('gender'),
            age=profile_data.get('age'),
            phone_number=profile_data.get('phone_number'),
            wants_texts=profile_data.get('wants_texts'),
        )

        img_url = validated_data.get('image_url', None)
        if img_url:
            profile.pic_url = validated_data['image_url']
            profile.save()

        return user

    def update(self, instance, validated_data):
        user = instance
        user.email = validated_data['email']
        user.password = validated_data['password']
        user.username = validated_data['username']
        return user


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('pic_url',)


class MatchSerializer(serializers.ModelSerializer):
    park_name = serializers.ReadOnlyField(source='park.name')
    creator_name = serializers.ReadOnlyField(source='creator.username')
    time = serializers.TimeField(format="%I:%M %p")
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
    park_name = serializers.ReadOnlyField(source='park.name')

    class Meta:
        model = Court
        fields = ('id', 'park', 'park_name', 'sport', 'other',
                  'num_courts')
        # extra_kwargs = {'location': {'write_only': True}}

    def create(self, validated_data):
        court = Court.objects.create(
            park=validated_data['park'],
            sport=validated_data['sport'],
            other=validated_data['other'],
            num_courts=validated_data['num_courts'],
        )
        lat = validated_data.get('lat', None)
        long = validated_data.get('long', None)
        if lat and long:
            court.location = 'POINT(' + str(validated_data['long']) + ' ' + str(validated_data['lat']) + ')'
            court.save()

        return court


class ParkSerializer(serializers.ModelSerializer):
    match_set = MatchSerializer(many=True, read_only=True)
    court_set = CourtSerializer(many=True, read_only=True)
    distance = serializers.DecimalField(source='distance.mi', max_digits=10, decimal_places=2, required=False, read_only=True)

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
