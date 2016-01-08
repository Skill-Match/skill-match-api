import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from django.core.management import BaseCommand
from matchup.models import HendersonPark, Ammenity


class Command(BaseCommand):

    def handle(self, *args, **options):
        r1 = requests.get('http://www.cityofhenderson.com/henderson-'
                          'happenings/parks-and-trails/locations-and-features')

        soup = BeautifulSoup(r1.content, 'html.parser')
        park_list = soup.find('ul', class_="sfNavVertical sfNavList")
        park_urls = []
        for park in park_list.find_all('li'):
            park_urls.append('http://www.cityofhenderson.com' +
                             park.a.get('href'))

        count = 0
        amm_count = 0
        for park_url in park_urls:
            response = requests.get(park_url)
            s5 = BeautifulSoup(response.content, 'html.parser')

            name = s5.h1.find_next_sibling('h2').string

            address_block = s5.find('div', class_='sfContentBlock').contents[0]
            if address_block.name == 'p':
                address = address_block.contents[0]
            else:
                if address_block == NavigableString:
                    address = address_block

            img = s5.find('div', id='page-box').img

            already_exists = HendersonPark.objects.filter(name=name)
            if not already_exists:
                this_park = HendersonPark.objects.create(name=name,
                                                         url=park_url,
                                                         address=address)
                if img:
                    img_src = 'http://www.cityofhenderson.com' + img['src']
                    this_park.img_url = img_src
                    this_park.save()

                count += 1

                h3_s = s5.find_all('h3')
                amm_h3 = None
                for h3 in h3_s:
                    if h3.string == 'Park amenities' or h3.string == \
                            'Park Amenities':
                        amm_h3 = h3
                if amm_h3:
                    amm_ul = amm_h3.find_next_sibling('ul')
                    for li in amm_ul.find_all('li'):
                        if li.a:
                            if type(li.contents[0]) == Tag:
                                ammenity_name = li.a.string
                            else:
                                ammenity_name = li.contents[0] + li.a.string
                        else:
                            ammenity_name = li.string
                        ammenity_exists = Ammenity.objects.filter(
                                name=ammenity_name)
                        if ammenity_exists:
                            ammenity = ammenity_exists[0]
                        else:
                            ammenity = Ammenity.objects.create(
                                    name=ammenity_name)
                            amm_count += 1
                        ammenity.parks.add(this_park)
                        ammenity.save()

        self.stdout.write("{} Henderson Parks {} Ammenities added to Database"
                          .format(count, amm_count))
