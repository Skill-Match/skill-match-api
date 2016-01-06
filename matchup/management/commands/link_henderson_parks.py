from django.core.management import BaseCommand
from matchup.models import Park, HendersonPark


class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        parks = Park.objects.filter(city__icontains='henderson')
        for park in parks:
            h_park = HendersonPark.objects.filter(name__icontains=park.name)
            if len(h_park) == 1:
                h_park = h_park[0]
                if not h_park.park:
                    h_park.park = park
                    h_park.save()
                    count += 1
        count2 = 0
        h_parks = HendersonPark.objects.all()
        for h_park in h_parks:
            if not h_park.park:
                park = Park.objects.filter(name__icontains=h_park.name)
                if len(park) == 1:
                    park = park[0]
                    h_park.park = park
                    h_park.save()
                    count2 += 1

        self.stdout.write("{} Parks added, {} parks using reverse".format(count, count2))