from django.core.management import BaseCommand
from matchup.models import Park
import oauth2
import requests
from skill_match.settings import YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET, \
    YELP_TOKEN, YELP_TOKEN_SECRET


class Command(BaseCommand):
    """
        Takes zip_code as an argument, pings yelp's api for the parks in that
            area, and adds the data from those parks to the database as Park
            Objects.
    """
    def handle(self, *args, **options):
        """
        :param args: zip_code ex. 89123
        :param options:
        :return: Writes out how many parks added to database
        """

        url = 'http://api.yelp.com/v2/search/' + '?location=' + \
              options['zip_code'][0] + ', NV &category_filter=parks'

        consumer = oauth2.Consumer(YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET)
        oauth_request = oauth2.Request(method="GET", url=url)

        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': YELP_TOKEN,
                'oauth_consumer_key': YELP_CONSUMER_KEY
            }
        )
        token = oauth2.Token(YELP_TOKEN, YELP_TOKEN_SECRET)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                                   consumer, token)
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
                if len(d_list) > 1:
                    d2 = d_list[1]
                else:
                    d2 = None
                if len(d_list) > 2:
                    d3 = d_list[2]
                else:
                    d3 = None
                park_rating = park['rating']
                park_image_url = park.get('image_url', None)
                park_rating_img_url = park['rating_img_url']
                park_rating_img_url_small = park['rating_img_url_small']
                park_city = park['location']['city']
                park_yelp_url = park['url']
                park_postal_code = park['location']['postal_code']
                park_latitude = park['location']['coordinate']['latitude']
                park_longitude = park['location']['coordinate']['longitude']
                park_state_code = park['location']['state_code']
                park = Park.objects.create(
                    rating=park_rating,
                    rating_img_url=park_rating_img_url,
                    rating_img_url_small=park_rating_img_url_small,
                    name=park_name,
                    url=park_yelp_url,
                    postal_code=park_postal_code,
                    city=park_city,
                    display_address1=d1,
                    display_address2=d2,
                    display_address3=d3,
                    location='POINT(' + str(park_longitude) + ' ' +
                             str(park_latitude) + ')',
                    state_code=park_state_code
                )
                if park_image_url:
                    park.image_url = park_image_url
                    park.save()
                count += 1

        self.stdout.write("{} Parks Added to Database".format(count))
