from django.contrib.auth.models import User
from matchup.models import Park, Match, Feedback, Skill, Court
from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from users.models import Profile


# USER RELATED SERIALIZERS
#
#
#
#
#
#
# USER RELATED SERIALIZERS


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ('sport', 'skill', 'num_feedbacks')
        read_only_fields = ('sport', 'skill', 'num_feedbacks')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('gender', 'age', 'phone_number', 'wants_texts',
                  'pic_url', 'small_pic_url', 'sportsmanship')

        read_only_fields = ('pic_url', 'small_pic_url', 'sportsmanship')


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
        """Overwrite to create profile during create process"""
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

        return user

    def update(self, instance, validated_data):
        user = instance
        user.email = validated_data['email']
        user.password = validated_data['password']
        user.username = validated_data['username']
        return user


class SimpleUserSerializer(serializers.ModelSerializer):
    skill_set = SkillSerializer(many=True, read_only=True)
    small_img = serializers.ReadOnlyField(source='profile.small_pic_url')

    class Meta:
        model = User
        fields = ('id', 'username', 'small_img', 'skill_set')
        read_only_fields = ('id', 'username', 'small_img', 'skill_set')

# """
# MATCH AND FEEDBACK RELATED SERIALIZERS
#
#
#
#
#
# """


class MatchSerializer(serializers.ModelSerializer):
    park_name = serializers.ReadOnlyField(source='park.name')
    creator_name = serializers.ReadOnlyField(source='creator.username')
    time = serializers.TimeField(format="%I:%M %p")
    players = SimpleUserSerializer(many=True, read_only=True)
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
        """
        Creating User is passed and added to the players(ManyToMany) on Match
        :param validated_data:
        :return:
        """
        match = super().create(validated_data)
        creator = validated_data['creator']
        match.players.add(creator)
        match.save()
        return match


class ChallengerMatchSerializer(serializers.ModelSerializer):
    """
        Separate Serializer for Simple Match Updates
    """
    class Meta:
        model = Match
        fields = ('id', 'creator', 'description', 'park', 'sport',
                  'skill_level', 'date', 'time', 'players',
                  'is_open', 'is_completed', 'is_confirmed')
        read_only_fields = ('id', 'creator', 'description', 'park', 'sport',
                            'skill_level', 'date', 'time', 'players',
                            'is_open', 'is_completed', 'is_confirmed')


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'reviewer', 'player', 'match', 'skill',
                  'sportsmanship', 'punctuality', 'availability')
        read_only_fields = ('id', 'reviewer', 'player',)

# PARK AND COURT RELATED SERILAIZERS
#
#
#
#
#
#
#


class CourtSerializer(serializers.ModelSerializer):
    """
    COURT serialiers are locations where a certain Sport is being played
    """
    park_name = serializers.ReadOnlyField(source='park.name')

    class Meta:
        model = Court
        fields = ('id', 'park', 'park_name', 'sport', 'other',
                  'num_courts', 'img_url', 'small_sport_img')
        read_only_fields = ('id', 'img_url', 'small_sport_img', 'park_name')
        # extra_kwargs = {'location': {'write_only': True}}

    def create(self, validated_data):
        """
        Overwrite create function in order to add POINTField
        :param validated_data:
        :return:
        """
        court = Court.objects.create(
            park=validated_data['park'],
            sport=validated_data['sport'],
            other=validated_data['other'],
            num_courts=validated_data['num_courts'],
            img_url=validated_data['img_url']
        )
        lat = validated_data.get('lat', None)
        long = validated_data.get('long', None)
        if lat and long:
            court.location = 'POINT(' + str(validated_data['long']) + ' ' + str(validated_data['lat']) + ')'
            court.save()

        return court


class ImageCourtSerializer(serializers.ModelSerializer):
    # Lighter Serializer for images
    class Meta:
        model = Court
        fields = ('sport', 'img_url', 'small_sport_img')
        read_only_fields = ('sport', 'img_url', 'small_sport_img')


class ParkSerializer(serializers.ModelSerializer):
    match_set = MatchSerializer(many=True, read_only=True)
    court_set = ImageCourtSerializer(many=True, read_only=True)
    distance = serializers.DecimalField(source='distance.mi', max_digits=10, decimal_places=2, required=False, read_only=True)

    class Meta:
        model = Park
        fields = ('id', 'name', 'rating', 'url', 'image_url', 'city', 'state_code',
                  'display_address1', 'display_address2', 'display_address3',
                  'postal_code', 'distance', 'match_set', 'latitude', 'longitude', 'court_set',)
        read_only_fields = ('id', 'name', 'rating', 'url', 'image_url', 'city', 'state_code',
                            'display_address1', 'display_address2',
                            'display_address3', 'postal_code')


class ListParksSerializer(serializers.ModelSerializer):
    # Separate Serializer to not include match_set
    court_set = ImageCourtSerializer(many=True, read_only=True)
    distance = serializers.DecimalField(source='distance.mi', max_digits=10, decimal_places=2, required=False, read_only=True)

    class Meta:
        model = Park
        fields = ('id', 'name', 'rating', 'url', 'image_url', 'city', 'state_code',
                  'display_address1', 'display_address2', 'display_address3',
                  'postal_code', 'distance', 'latitude', 'longitude', 'court_set',)
        read_only_fields = ('id', 'name', 'rating', 'url', 'image_url', 'city', 'state_code',
                            'display_address1', 'display_address2',
                            'display_address3', 'postal_code')


