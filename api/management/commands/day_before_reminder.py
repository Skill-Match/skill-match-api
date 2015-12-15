from datetime import timedelta, date, datetime
from api.notifications import twenty_four_hour_notify
from django.core.management import BaseCommand
from matchup.models import Match


class Command(BaseCommand):

    def handle(self, *args, **options):
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


# from datetime import timedelta, datetime
# from api.calculations import calculate_skills
# from django.core.management import BaseCommand
# from matchup.models import Feedback, Skill
#
#
# class Command(BaseCommand):
#     def add_arguments(self, parser):
#         pass
#
#     def handle(self, *args, **options):
#         one_hour = timedelta(hours=1)
#         new_feedbacks = Feedback.objects.filter(created_at__gt=
#                                                 (datetime.now() - one_hour))
#
#         num_updates = 0
#         for feedback in new_feedbacks:
#             player = feedback.player
#             sport = feedback.match.sport
#             feedback_count = Feedback.objects.filter(match__sport=sport).\
#                 filter(player=player).count()
#             skill = Skill.objects.filter(player=player).filter(sport=sport)
#
#             #Update Skill every 3 matches to keep feedback anonymous
#             if feedback_count % 3 == 0:
#                 if skill:
#                     skill = skill[0]
#                     calculate_skills(skill, sport)
#                     num_updates += 1
#                 else:
#                     new_skill = Skill.objects.create(player=player, sport=sport)
#                     calculate_skills(new_skill, sport)
#                     num_updates += 1
#
#         self.stdout.write("{} Skills updated".format(num_updates))