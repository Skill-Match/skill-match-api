from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from matchup.models import Match, Park
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
        self.assertEqual((response_park_list['name'], self.park.name))

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
        self.match = Match.objects.create(creator=self.user)