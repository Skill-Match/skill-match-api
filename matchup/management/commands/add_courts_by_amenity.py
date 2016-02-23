from django.core.management import BaseCommand
from django.db.models import Count
from matchup.models import Park, Court


class Command(BaseCommand):
    """
        This command creates Court objects with a foreign key to Park objects
        if the park has a related HendersonPark and if the amenity set for
        that HendersonPark contains the sport name for that sport. For example,
        A Tennis Court object is created if the park, Mesa Park is Linked to a
        HendersonPark with an Amenity, such as, 'Lighted Tennis Courts'. The
        Court object is created with a foreign key to that park.
    """
    def handle(self, *args, **options):

        # Only get parks with a related Henderson Park
        parks = Park.objects.annotate(count=Count('henderson_park')).\
            exclude(count=0)
        counter = 0
        for park in parks:
            h_park = park.henderson_park.all()[0]
            if h_park.ammenity_set.filter(name__icontains='tennis'):
                if not park.court_set.filter(sport='Tennis'):
                    Court.objects.create(park=park, sport='Tennis')
                    counter += 1
            if h_park.ammenity_set.filter(name__icontains='basketball'):
                if not park.court_set.filter(sport='Basketball'):
                    Court.objects.create(park=park, sport='Basketball')
                    counter += 1
            if h_park.ammenity_set.filter(name__icontains='volleyball'):
                if not park.court_set.filter(sport='Volleyball'):
                    Court.objects.create(park=park, sport='Volleyball')
                    counter += 1
            if h_park.ammenity_set.filter(name__icontains='pickleball'):
                if not park.court_set.filter(sport='Pickleball'):
                    Court.objects.create(park=park, sport='Pickleball')
                    counter += 1
            if h_park.ammenity_set.filter(name__icontains='multi-purpose '
                                                          'field'):
                if not park.court_set.filter(sport='Football'):
                    Court.objects.create(park=park, sport='Football')
                    counter += 1
                if not park.court_set.filter(sport='Soccer'):
                    Court.objects.create(park=park, sport='Soccer')
                    counter += 1

        self.stdout.write("{} Courts added".format(counter))
