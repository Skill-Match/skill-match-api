from datetime import date, time, datetime
from django.core.management import BaseCommand
from matchup.models import Match


class Command(BaseCommand):
    def handle(self, *args, **options):
        today = date.today()
        now = datetime.now()
        matches = Match.objects.filter(date__lt=today)
        count = 0
        for match in matches:
            match_datetime = datetime.combine(match.date, match.time)
            if match_datetime < now:
                match.is_completed = True
                match.save()
                count += 1

        self.stdout.write("{} Matches completed".format(count))