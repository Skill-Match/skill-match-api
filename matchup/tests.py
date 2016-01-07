from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.test import TestCase
from matchup.models import Match, Park, Feedback, Court, HendersonPark, \
    Ammenity
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Profile, Skill
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

    def test_detail_park(self):
        url = reverse('api_park_detail', kwargs={'pk': self.park.id})
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.park.name)


class MatchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        self.user2 = User.objects.create_user(username='bob',
                                             email='test1@test.com',
                                             password='password')
        self.user3 = User.objects.create_user(username='sarah',
                                             email='test2@test.com',
                                             password='password')
        Profile.objects.create(user=self.user, gender='Male', age="20's",
                               wants_texts=False, phone_number="5082693675")
        Profile.objects.create(user=self.user2, gender='Male', age="30's",
                               wants_texts=False)
        Profile.objects.create(user=self.user3, gender='Female', age="20's",
                               wants_texts=False)
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
        self.match = Match.objects.create(creator=self.user,
                                          park=self.park,
                                          sport='Tennis',
                                          skill_level=80,
                                          date='2016-2-22',
                                          time='18:30',
                                          )
        self.match2 = Match.objects.create(creator=self.user,
                                           park=self.park2,
                                           sport='Basketball',
                                           skill_level=60,
                                           date='2016-2-25',
                                           time='9:00')
        self.match3 = Match.objects.create(creator=self.user2,
                                           park=self.park3,
                                           sport='Tennis',
                                           skill_level=75,
                                           date='2016-3-3',
                                           time='12:00')
        self.match.players.add(self.user)
        self.match2.players.add(self.user)
        self.match3.players.add(self.user2)
        self.match.save()
        self.match2.save()
        self.match3.save()

    def test_list_matches(self):
        # Again not testing if they return in the order requested (location)
        url = reverse('api_list_create_matches')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        url2 = reverse('api_list_create_matches') + '?sport=basketball'
        response2 = self.client.get(url2, {}, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['count'], 1)
        basketball_match = response2.data['results'][0]
        self.assertEqual(basketball_match['sport'], 'Basketball')
        url3 = reverse('api_list_create_matches') + '?username=' + self.user.username
        response3 = self.client.get(url3, {}, format='json')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.data['count'], 2)
        url4 = reverse('api_list_create_matches') + '?zip=89123'
        response4 = self.client.get(url4, {}, format='json')
        self.assertEqual(response4.status_code, status.HTTP_200_OK)
        self.assertEqual(response4.data['count'], 3)
        url5 = reverse('api_list_create_matches') + '?lat=36.169941&long=-115.139830'
        response5 = self.client.get(url5, {}, format='json')
        self.assertEqual(response5.status_code, status.HTTP_200_OK)
        self.assertEqual(response5.data['count'], 3)
        url6 = reverse('api_list_create_matches') + '?home=home'
        response6 = self.client.get(url6, {}, format='json')
        self.assertEqual(response6.status_code, status.HTTP_200_OK)
        self.assertEqual(response6.data['count'], 3)

    def test_create_match(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_list_create_matches')
        data = {'park': self.park.id, 'sport': 'Tennis', 'skill_level': 35,
                'date': '2016-2-2', 'time': '12:00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Match.objects.count(), 4)
        self.assertEqual(response.data['sport'], 'Tennis')
        self.assertEqual(response.data['is_open'], True)
        self.assertEqual(response.data['skill_level'], 35)

    def test_create_challenge_match(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_challenge')
        data = {'park': self.park.id, 'sport': 'Tennis', 'skill_level': 55,
                'date': '2016-2-2', 'time': '1:00', 'challenge': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['skill_level'], 55)
        self.assertEqual(response.data['is_open'], False)
        self.assertEqual(response.data['is_challenge'], True)

    def test_join_confirm_match(self):
        #join
        self.client.force_authenticate(user=self.user2)
        url = reverse('api_join_match', kwargs={'pk': self.match.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match.players.count(), 2)
        self.assertEqual(response.data['is_open'], False)
        #confirm
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

    def test_multiple_join_match(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('api_join_match', kwargs={'pk': self.match2.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match2.players.count(), 2)
        self.assertEqual(response.data['is_open'], True)
        self.client.force_authenticate(user=self.user3)
        url = reverse('api_join_match', kwargs={'pk': self.match2.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.match2.players.count(), 3)
        self.assertEqual(response.data['is_open'], True)

    def test_detail_update_match(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_detail_update_match', kwargs={'pk': self.match.id})
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['skill_level'], self.match.skill_level)
        data = {'park': self.park.id, 'sport': 'Tennis', 'skill_level': 35,
                'date': '2016-2-2', 'time': '12:00'}
        response2 = self.client.put(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['skill_level'], 35)


class FeedbackTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        self.user2 = User.objects.create_user(username='bob',
                                              email='test1@test.com',
                                              password='password')
        Profile.objects.create(user=self.user, gender='Male', age="20's",
                               wants_texts=False, phone_number="5082693675")
        Profile.objects.create(user=self.user2, gender='Male', age="30's",
                               wants_texts=False)
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
        self.match = Match.objects.create(creator=self.user,
                                          park=self.park,
                                          sport='Tennis',
                                          skill_level=80,
                                          date='2016-2-22',
                                          time='18:30',
                                          )
        self.match2 = Match.objects.create(creator=self.user,
                                           park=self.park2,
                                           sport='Basketball',
                                           skill_level=60,
                                           date='2016-2-25',
                                           time='9:00')
        self.match.players.add(self.user)
        self.match.players.add(self.user2)
        self.match2.players.add(self.user)
        self.match.save()
        self.match2.save()

        self.feedback = Feedback.objects.create(reviewer=self.user,
                                                player=self.user2,
                                                match=self.match2,
                                                skill=70,
                                                sportsmanship=80,
                                                punctuality='On Time',
                                                availability=3)

    def test_create_feedback(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_create_feedback')
        data = {'match': self.match.id, 'skill': 50, 'sportsmanship': 90,
                'punctuality': 'On Time', 'availability': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 2)
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
        self.assertEqual(Feedback.objects.count(), 2)
        self.assertEqual(response.data['skill'], 50)
        self.assertEqual(response.data['punctuality'], 'On Time')
        self.assertEqual(response.data['player'], self.user2.id)

    def test_detail_update_feedback(self):
        self.client.force_authenticate(user=self.user)
        self.client.force_login(user=self.user)
        url = reverse('api_detail_update_feedback', kwargs={'pk': self.feedback.id})
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['skill'], self.feedback.skill)
        data = {'match': self.match2.id, 'skill': 50, 'sportsmanship': 90,
                'punctuality': 'On Time', 'availability': 5,
                'player': self.user2.id}
        response2 = self.client.put(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['skill'], 50)


class CourtTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
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
        self.court = Court.objects.create(park=self.park, sport="Tennis")

    def test_simple_create_court(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_create_courts')
        data = {'park': self.park.id, 'sport': 'Basketball'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sport'], 'Basketball')
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_court_by_location(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_create_courts')
        data = {'park': self.park.id, 'sport': 'Other', 'other': 'Disc Golf',
                'lat': '42.123650', 'long': '-71.178624', 'num_courts': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['other'], 'Disc Golf')

    def detail_update_court(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_detail_update_court', kwargs={'pk': self.court.id})
        data = {'park': self.park.id, 'sport': 'Tennis',
                'lat': '42.123650', 'long': '-71.178624', 'num_courts': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num_courts'], 2)

class SkillTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        self.user2 = User.objects.create_user(username='bob',
                                             email='test1@test.com',
                                             password='password')
        self.user3 = User.objects.create_user(username='sarah',
                                             email='test2@test.com',
                                             password='password')
        Profile.objects.create(user=self.user, gender='Male', age="20's",
                               wants_texts=False, phone_number="5082693675")
        Profile.objects.create(user=self.user2, gender='Male', age="30's",
                               wants_texts=False)
        Profile.objects.create(user=self.user3, gender='Female', age="20's",
                               wants_texts=False)
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
        self.match = Match.objects.create(creator=self.user,
                                          park=self.park,
                                          sport='Tennis',
                                          skill_level=80,
                                          date='2016-2-22',
                                          time='18:30',
                                          )
        self.match2 = Match.objects.create(creator=self.user,
                                           park=self.park,
                                           sport='Tennis',
                                           skill_level=60,
                                           date='2016-2-25',
                                           time='9:00')
        self.match3 = Match.objects.create(creator=self.user2,
                                           park=self.park,
                                           sport='Tennis',
                                           skill_level=75,
                                           date='2016-3-3',
                                           time='12:00')
        self.match.players.add(self.user)
        self.match.players.add(self.user2)
        self.match2.players.add(self.user)
        self.match2.players.add(self.user2)
        self.match3.players.add(self.user2)
        self.match3.players.add(self.user3)
        self.match.save()
        self.match2.save()
        self.match3.save()

        Feedback.objects.create(reviewer=self.user, player=self.user2,
                                match=self.match, skill=90, sportsmanship=90,
                                availability=5, punctuality='On Time')
        Feedback.objects.create(reviewer=self.user2, player=self.user,
                                match=self.match, skill=80, sportsmanship=80,
                                availability=5, punctuality='On Time')
        Feedback.objects.create(reviewer=self.user, player=self.user2,
                                match=self.match2, skill=90, sportsmanship=90,
                                availability=5, punctuality='On Time')
        Feedback.objects.create(reviewer=self.user2, player=self.user,
                                match=self.match2, skill=80, sportsmanship=80,
                                availability=5, punctuality='On Time')
        Feedback.objects.create(reviewer=self.user3, player=self.user,
                                match=self.match3, skill=10, sportsmanship=10,
                                availability=5, punctuality='On Time')

        self.skill = Skill.objects.create(player=self.user, sport='Tennis')
        self.skill2 = Skill.objects.create(player=self.user2, sport='Tennis')
        self.skill2.calculate()
        self.skill2.save()
        self.skill.calculate()
        self.skill.save()

    def test_calculate_skill(self):
        self.assertEqual(self.skill.skill, 66.29)


class CommandsTests(TestCase):
    def test_add_parks(self):
        args = ['89148']
        call_command('add_parks', args)
        park_count = Park.objects.count()
        self.assertEqual(park_count, 20)

    def test_add_henderson_parks(self):
        call_command('add_henderson_parks')
        park_count = HendersonPark.objects.count()
        ammenities_count = Ammenity.objects.count()
        ammenities = False
        parks = False
        if park_count > 0:
            parks = True
        if ammenities_count > 0:
            ammenities = True
        self.assertEqual(parks, True)
        self.assertEqual(ammenities, True)

    def test_link_henderson_parks(self):
        call_command('add_parks', ['89074'])
        call_command('add_henderson_parks')
        call_command('link_henderson_parks')
        parks = Park.objects.annotate(count=Count('henderson_park')).exclude(count=0)
        count = parks.count()
        linked_parks = False
        if count > 0:
            linked_parks = True
        self.assertEqual(linked_parks, True)

    def test_courts_by_ammenity(self):
        call_command('add_parks', ['89074'])
        call_command('add_henderson_parks')
        call_command('link_henderson_parks')
        call_command('add_courts_by_ammenity')
        count = Court.objects.count()
        courts = False
        if count > 0:
            courts = True
        self.assertEqual(courts, True)

    # def test_close_completed_matches(self):
    #     user = User.objects.create_user(username='peter',
    #                                     email='test@test.com',
    #                                     password='pwd')
    #     user2 = User.objects.create_user(username='bob',
    #                                     email='test2@test.com',
    #                                     password='pwd')
    #     park = Park.objects.create(name='Test Park',
    #                                     rating=4.0,
    #                                     url="www.testpark.com",
    #                                     image_url='www.imageurl.com',
    #                                     rating_img_url='www.rating.com',
    #                                     rating_img_url_small='www.ratimg.com',
    #                                     city='Boston',
    #                                     state_code='MA',
    #                                     display_address1='10 Happy St.',
    #                                     display_address2='Downtown',
    #                                     display_address3='Boston, MA 02121',
    #                                     postal_code='02121',
    #                                     location=BOSTON_LOC)
    #     match = Match.objects.create(creator=user, park=park, sport='Tennis',
    #                          skill_level=50, date='2015-12-31', time='15:00',
    #                          is_open=False)
    #     match.players.add(user)
    #     match.players.add(user2)
    #     match.save()
    #     self.assertEqual(match.is_completed, False)
    #     call_command('close_completed_matches')
    #     self.assertEqual(match.is_completed, True)