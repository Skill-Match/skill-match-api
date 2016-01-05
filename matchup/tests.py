from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from matchup.models import Match, Park, Feedback, Court
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Profile
from django.contrib.gis.geos import GEOSGeometry as G


LAS_VEGAS_LOC = G('POINT(-115.13983 36.169941)', srid=4326)
BOSTON_LOC = G('POINT(-71.05888 42.360082)', srid=4326)
SHARON_MA_LOC = G('POINT(-71.178624 42.123650)', srid=4326)

class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        Profile.objects.create(user=self.user, gender='Male', age="30's",
                               wants_texts=True)

    def test_created_token(self):
        self.assertEqual(hasattr(self.user, 'auth_token'), True)

    def test_obtain_auth_token(self):
        data = {"username": self.user.username, "password": 'password'}
        url = reverse('api_obtain_auth_token')
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['user_id'], self.user.id)

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
        Profile.objects.create(user=self.user, gender='Male', age="20's",
                               wants_texts=False, phone_number="5082693675")

        self.park = Park.objects.create(name='Test Park',
                                        rating=4.0,
                                        url="www.testpark.com",
                                        image_url='www.imageurl.com',
                                        rating_img_url='www.rating.com',
                                        rating_img_url_small='www.ratimg.com',
                                        city='Boston',
                                        state_code='MA',
                                        display_address1='10 Happy St.',
                                        display_address2='Downtown',
                                        display_address3='Boston, MA 02121',
                                        postal_code='02121',
                                        location=BOSTON_LOC)
        self.park2 = Park.objects.create(name='Test Park2',
                                         rating=3.0,
                                         url="www.testpark2.com",
                                         image_url='www.imageurl2.com',
                                         rating_img_url='www.rating2.com',
                                         rating_img_url_small='www.rtimg2.com',
                                         city='Las Vegas',
                                         state_code='NV',
                                         display_address1='12 Happy St.',
                                         display_address2='Suburb',
                                         display_address3='Las Vegas, NV',
                                         postal_code='89148',
                                         location=LAS_VEGAS_LOC)
        self.park3 = Park.objects.create(name='Test Park3',
                                         rating=5.0,
                                         url="www.testpark3.com",
                                         image_url='www.imageurl3.com',
                                         rating_img_url='www.rating3.com',
                                         rating_img_url_small='www.rtimg3.com',
                                         city='Sharon',
                                         state_code='MA',
                                         display_address1='16 High St.',
                                         display_address2='Suburb',
                                         display_address3='Sharon, MA 02067',
                                         postal_code='02067',
                                         location=SHARON_MA_LOC)

        self.court = Court.objects.create(park=self.park, sport="Tennis")
        self.court2 = Court.objects.create(park=self.park3, sport="Basketball")

    def test_list_parks(self):
        # Not sure how to test that parks are coming back in the right order
        url = reverse('api_list_parks')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        url2 = reverse('api_list_parks') + '?search=park2'
        response2 = self.client.get(url2, {}, format='json')
        response_park2 = response2.data['results'][0]
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_park2['name'], self.park2.name)
        url3 = reverse('api_list_parks') + '?sport=tennis'
        response3 = self.client.get(url3, {}, format='json')
        response_park3 = response3.data['results'][0]
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(response_park3['name'], self.park.name)
        url4 = reverse('api_list_parks') + '?courts=True'
        response4 = self.client.get(url4, {}, format='json')
        self.assertEqual(response4.status_code, status.HTTP_200_OK)
        self.assertEqual(response4.data['count'], 2)
        url5 = reverse('api_list_parks') + '?zip_code=02112'
        response5 = self.client.get(url5, {}, format='json')
        self.assertEqual(response5.status_code, status.HTTP_200_OK)
        self.assertEqual(response5.data['count'], 3)
        url6 = reverse('api_list_parks') + '?lat=36.169941&long=-115.139830'
        response6 = self.client.get(url6, {}, format='json')
        self.assertEqual(response6.status_code, status.HTTP_200_OK)
        self.assertEqual(response6.data['count'], 3)


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
                                          time='18:23',)
        self.match.players.add(self.user)
        self.match.players.add(self.user2)
        self.match.save()

    def test_create_feedback(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_create_feedback')
        data = {'match': self.match.id, 'skill': 50, 'sportsmanship': 90,
                'punctuality': 'On Time', 'availability': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(response.data['skill'], 50)
        self.assertEqual(response.data['punctuality'], 'On Time')

    def test_create_feeback_player(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_create_feedback')
        data = {'match': self.match.id, 'skill': 50, 'sportsmanship': 90,
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