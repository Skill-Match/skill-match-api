from django.core.management import BaseCommand
from datetime import date
from matchup.models import Park
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator


class Command(BaseCommand):

    def handle(self, *args, **options):

        auth = Oauth1Authenticator(
        consumer_key="J_lQomBe-LKch6QM6lp_4Q",
        consumer_secret="uvPNl74cDNK23h9KeWWDPGCJ0rA",
        token="Dxa-Yr4Zbf7dG52CHqxYAc5KpgDrdX62",
        token_secret="8eJm_JtFMSkmt9hAWMYRp-uew3o"
        )

        params = {"category_filter": "parks"}
        client = Client(auth)
        r = client.search('89148', **params)
        parks = r.businesses

        count = 0
        for park in parks:
            park_exists = Park.objects.filter(name=park.name)
            if len(park_exists) == 0:
                d_list = park.location.display_address
                d1 = d_list[0]
                d2 = d_list[1]
                if len(d_list) > 2:
                    d3 = d_list[2]
                else:
                    d3 = None
                Park.objects.create(
                    rating=park.rating.rating,
                    mobile_url=park.mobile_url,
                    review_count=park.review_count,
                    name=park.name,
                    url=park.url,
                    image_url=park.image_url,
                    city=park.location.city,
                    display_address1=d1,
                    display_address2=d2,
                    display_address3=d3,
                    postal_code=park.location.postal_code,
                    latitude=park.location.coordinate.latitude,
                    longitude=park.location.coordinate.longitude,
                    state_code=park.location.state_code
                )
                count += 1

        self.stdout.write("{} Parks Added to Database".format(count))

    # def handle(self, *args, **options):
    #     """
    #     This method is required to be overridden. It is the main source of code
    #     :param args:
    #     :param options:
    #     :return:
    #     """
    #     count = 0
    #     for wishlist in WishList.objects.all():
    #         if wishlist.expiration <= date.today() and not wishlist.is_expired:
    #             wishlist.close()
    #             count += 1
    #
    #     self.stdout.write("{} Lists closed".format(count))