from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from matchup.models import Match, Park, Feedback
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Profile


class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        Profile.objects.create(user=self.user, gender='Male', age="30's",
                               wants_texts=True)

    def test_create_token(self):
        self.assertEqual(hasattr(self.user, 'auth_token'), True)

    def test_list_users(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_list_users')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        response_user_list = response.data['results'][0]
        self.assertEqual(response_user_list['username'], self.user.username)

    def test_create_user_profile_token(self):
        url = reverse('api_create_user')
        data = {'username': 'bob', 'email': 'email@email.com', 'password':
                'pwd', 'profile': {'gender': "Male", 'age': "20's",
                                   'wants_texts': False}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['username'], 'bob')
        self.assertEqual(response.data['profile']['gender'], 'Male')
        bob = User.objects.get(username='bob')
        self.assertEqual(hasattr(bob, 'auth_token'), True)

    def test_detail_update_user(self):
        url = reverse('api_detail_update_user', kwargs={'pk': self.user.id})
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        response = self.client.put(url, {'username': 'bob', 'email': 'email@email.com', 'password':
                'pwd', 'profile': {'gender': "Male", 'age': "20's", "phone_number": "",
                                   'wants_texts': False}}, format='json')
        self.assertEqual(response.data['username'], 'bob')
        self.assertEqual(response.data['profile']['age'], "20's")


class ParkTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password',)
        self.park = Park.objects.create(name='Test Park',
                                        postal_code='89148')
        Profile.objects.create(user=self.user, gender='Male', age="20's",
                               wants_texts=False, phone_number="5082693675")

    def test_list_parks(self):
        url = reverse('api_list_parks')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        response_park_list = response.data['results'][0]
        self.assertEqual(response_park_list['name'], self.park.name)


class MatchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        self.user2 = User.objects.create_user(username='bob',
                                             email='test@test.com',
                                             password='password')
        self.park = Park.objects.create(name='Test Park',
                                        postal_code='89148')
        self.match = Match.objects.create(creator=self.user,
                                          park=self.park,
                                          sport='Tennis',
                                          skill_level=80,
                                          date='2015-12-22',
                                          time='18:23',
                                          )
        self.match.players.add(self.user)
        self.match.save()
        Profile.objects.create(user=self.user, gender='Male', age="20's",
                               wants_texts=False, phone_number="5082693675")
        Profile.objects.create(user=self.user2, gender='Male', age="30's",
                               wants_texts=False)

    def test_list_matches(self):
        url = reverse('api_list_create_matches')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        response_matches_list = response.data['results'][0]
        self.assertEqual(response_matches_list['sport'], self.match.sport)
        self.assertEqual((response_matches_list['skill_level']), 80)

    def test_create_match(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_list_create_matches')
        data = {'park': self.park.id, 'sport': 'Tennis', 'skill_level': 35,
                'date': '2016-2-2', 'time': '12:00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Match.objects.count(), 2)
        self.assertEqual(response.data['sport'], 'Tennis')
        self.assertEqual(response.data['skill_level'], 35)

    def test_join_confirm_match(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('api_join_match', kwargs={'pk': self.match.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match.players.count(), 2)
        self.assertEqual(response.data['is_open'], False)

        self.client.force_authenticate(user=self.user)
        confirm_url = reverse('api_confirm_match', kwargs={'pk': self.match.id})
        response = self.client.put(confirm_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_confirmed'], True)

    def test_leave_match(self):
        self.client.force_authenticate(user=self.user2)
        self.match.players.add(self.user2)
        self.match.save()
        url = reverse('api_leave_match', kwargs={'pk': self.match.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match.players.count(), 1)
        self.assertEqual(response.data['is_open'], True)

    def test_decline_match(self):
        self.client.force_authenticate(user=self.user)
        self.match.players.add(self.user2)
        self.match.save()
        url = reverse('api_decline_match', kwargs={'pk': self.match.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_confirmed'], False)
        self.assertEqual(response.data['is_open'], True)


class FeedbackTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        self.user2 = User.objects.create_user(username='bob',
                                             email='test@test.com',
                                             password='password')
        self.park = Park.objects.create(name='Test Park',
                                        postal_code='89148')
        self.match = Match.objects.create(creator=self.user,
                                          park=self.park,
                                          sport='Tennis',
                                          skill_level=80,
                                          date='2015-12-22',
                                          time='18:23',
                                          )
        self.match.players.add(self.user)
        self.match.players.add(self.user2)
        self.match.save()

    def test_create_feedback(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_create_feedback')
        data = {'match': 1, 'skill': 50, 'sportsmanship': 90,
                'punctuality': 'On Time', 'availability': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(response.data['skill'], 50)
        self.assertEqual(response.data['punctuality'], 'On Time')

    def test_create_feeback_player(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_create_feedback')
        data = {'match': 1, 'skill': 50, 'sportsmanship': 90,
                'punctuality': 'On Time', 'availability': 5,
                'player': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(response.data['skill'], 50)
        self.assertEqual(response.data['punctuality'], 'On Time')
        self.assertEqual(response.data['player'], self.user2.id)

class CourtTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        self.user2 = User.objects.create_user(username='bob',
                                             email='test@test.com',
                                             password='password')
        self.park = Park.objects.create(name='Test Park',
                                        postal_code='89148')

    def test_create_court(self):
        pass

    def test_list_courts(self):
        pass