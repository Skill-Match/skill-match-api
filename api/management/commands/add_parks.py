from django.core.management import BaseCommand
from datetime import date
from matchup.models import Park
import oauth2
import requests
from skill_match.settings import CONSUMER_KEY, CONSUMER_SECRET, TOKEN, \
    TOKEN_SECRET


class Command(BaseCommand):
    """
        Takes zip_code as an argument, pings yelp's api for the parks in that
            area, and adds the data from those parks to the database as Park
            Objects.
    """

    def add_arguments(self, parser):
        parser.add_argument('zip_code', nargs='+', type=str)

    def handle(self, *args, **options):
        """

        :param args: zip_code ex. 89123
        :param options:
        :return: Writes out how many parks added to database
        """

        url = 'http://api.yelp.com/v2/search/' + '?location=' + \
              options['zip_code'][0] + ', NV &category_filter=parks'

        consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        oauth_request = oauth2.Request(method="GET", url=url)

        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': TOKEN,
                'oauth_consumer_key': CONSUMER_KEY
            }
        )
        token = oauth2.Token(TOKEN, TOKEN_SECRET)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        signed_url = oauth_request.to_url()
        response = requests.get(signed_url)
        content = response.json()
        parks = content['businesses']

        count = 0
        for park in parks:
            park_name = park['name']
            park_exists = Park.objects.filter(name=park_name)
            if len(park_exists) == 0:
                d_list = park['location']['display_address']
                d1 = d_list[0]
                d2 = d_list[1]
                if len(d_list) > 2:
                    d3 = d_list[2]
                else:
                    d3 = None
                park_rating = park['rating']
                park_mobile_url = park['mobile_url']
                park_image_url = park['image_url']
                park_id = park['id']
                park_city = park['location']['city']
                park_yelp_url = park['url']
                park_postal_code = park['location']['postal_code']
                park_latitude = park['location']['coordinate']['latitude']
                park_longitude = park['location']['coordinate']['longitude']
                park_state_code = park['location']['state_code']
                Park.objects.create(
                    rating=park_rating,
                    mobile_url=park_mobile_url,
                    image_url=park_image_url,
                    name=park_name,
                    yelp_id=park_id,
                    url=park_yelp_url,
                    postal_code=park_postal_code,
                    city=park_city,
                    display_address1=d1,
                    display_address2=d2,
                    display_address3=d3,
                    latitude=park_latitude,
                    longitude=park_longitude,
                    location='POINT(' + str(park_latitude) + ' ' + str(park_longitude) + ')',
                    state_code=park_state_code
                )
                count += 1

        self.stdout.write("{} Parks Added to Database".format(count))

# class Command(BaseCommand):
# **NOT NEEDED AT ALL** --> used for reference only
#
#     def handle(self, *args, **options):
#
#         auth = Oauth1Authenticator(
#         consumer_key="J_lQomBe-LKch6QM6lp_4Q",
#         consumer_secret="uvPNl74cDNK23h9KeWWDPGCJ0rA",
#         token="Dxa-Yr4Zbf7dG52CHqxYAc5KpgDrdX62",
#         token_secret="8eJm_JtFMSkmt9hAWMYRp-uew3o"
#         )
#
#         params = {"category_filter": "parks"}
#         client = Client(auth)
#         r = client.search('89148', **params)
#         parks = r.businesses
#
#         count = 0
#         for park in parks:
#             park_exists = Park.objects.filter(name=park.name)
#             if len(park_exists) == 0:
#                 d_list = park.location.display_address
#                 d1 = d_list[0]
#                 d2 = d_list[1]
#                 if len(d_list) > 2:
#                     d3 = d_list[2]
#                 else:
#                     d3 = None
#                 Park.objects.create(
#                     rating=park.rating.rating,
#                     mobile_url=park.mobile_url,
#                     review_count=park.review_count,
#                     name=park.name,
#                     url=park.url,
#                     image_url=park.image_url,
#                     city=park.location.city,
#                     display_address1=d1,
#                     display_address2=d2,
#                     display_address3=d3,
#                     postal_code=park.location.postal_code,
#                     latitude=park.location.coordinate.latitude,
#                     longitude=park.location.coordinate.longitude,
#                     state_code=park.location.state_code
#                 )
#                 count += 1
#
#         self.stdout.write("{} Parks Added to Database".format(count))
