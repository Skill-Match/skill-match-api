from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from matchup.models import Match, Park, Feedback
from rest_framework import status
from rest_framework.test import APITestCase


class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')

    def test_list_users(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_list_users')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        response_user_list = response.data['results'][0]
        self.assertEqual(response_user_list['username'], self.user.username)

    def test_create_user(self):
        url = reverse('api_create_user')
        data = {'username': 'bob', 'email': 'email@email.com', 'password':
                'pwd', 'profile': {'gender': 'Man', 'age': "20's"}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['username'], 'bob')
        self.assertEqual(response.data['profile']['gender'], 'Man')

    def test_detail_update_user(self):
        url = reverse('api_detail_update_user', kwargs={'pk': self.user.id})
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        # NEED TO ADD PUT


class ParkTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        self.park = Park.objects.create(name='Test Park',
                                        postal_code='89148')

    def test_list_parks(self):
        url = reverse('api_list_parks')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        response_park_list = response.data['results'][0]
        self.assertEqual(response_park_list['name'], self.park.name)

    def test_create_park(self):
        url = reverse('api_create_park')
        data = {'name': 'Test Park 2', 'postal_code': '89148'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Park.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Test Park 2')
        self.assertEqual(response.data['postal_code'], '89148')


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
        self.match.players.add(self.user, self.user2)
        self.match.save()

    def test_list_matches(self):
        url = reverse('api_list_create_matches')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        response_matches_list = response.data['results'][0]
        self.assertEqual(response_matches_list['sport'], self.match.sport)
        self.assertEqual((response_matches_list['skill_level']), 80)

    def test_create_match(self):
        url = reverse('api_list_create_matches')
        data = {'park': 1, 'sport': 'Tennis', 'skill_level': 35,
                'date': '2016-2-2', 'time': '12:00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Match.objects.count(), 2)
        self.assertEqual(response.data['sport'], 'Tennis')
        self.assertEqual(response.data['skill_level'], 35)

    def test_confirm_decline_signup_match(self):
        url = reverse('api_update_match', kwargs={'pk': self.match.id})
        self.client.force_authenticate(user=self.user)
        response1 = self.client.put(url, {'decline': 'true'}, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match.is_open, True)
        self.assertEqual(self.match.is_confirmed, False)
        self.client.force_authenticate(user=self.user2)
        response2 = self.client.put(url, {}, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match.is_open, False)
        response3 = self.client.put(url, {'confirm': 'true'}, format='json')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match.is_open, False)
        self.assertEqual(self.match.is_confirmed, True)



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

