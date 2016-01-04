from datetime import timedelta, date, datetime
from api.notifications import twenty_four_hour_notify
from django.core.management import BaseCommand
from matchup.models import Match


class Command(BaseCommand):

    def handle(self, *args, **options):
        """

        :param args:
        :param options:
        :return:
        """
        day = timedelta(days=1)
        twenty3_hours = timedelta(hours=23)
        matches = Match.objects.filter(is_completed=False)\
            .filter(is_confirmed=True)\
            .filter(date__lte=date.today() + day)\
            .filter(time__lt=datetime.now() + day)\
            .filter(time__gt=datetime.now() + twenty3_hours)

        count = 0
        for match in matches:
            twenty_four_hour_notify(match)
            count += 1

        self.stdout.write("{} Matches notified".format(count))
