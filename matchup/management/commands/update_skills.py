from datetime import timedelta, datetime
from django.core.management import BaseCommand
from matchup.models import Feedback
from users.models import Skill


class Command(BaseCommand):
    """
        Used with Heroku Scheduler to Update skills. Every hour, it checks to
        see if a recent Feedback has been left. To keep Feedback anonymous,
        Skills are only updated if the Feedback is the third Feedback.Y
    """

    def handle(self, *args, **options):
        one_hour = timedelta(hours=1)
        new_feedbacks = Feedback.objects.filter(created_at__gt=(
            datetime.now() - one_hour))

        num_updates = 0
        for feedback in new_feedbacks:
            player = feedback.player
            sport = feedback.match.sport
            feedback_count = Feedback.objects.filter(match__sport=sport).\
                filter(player=player).count()
            skill = Skill.objects.filter(player=player).filter(sport=sport)

            # Update Skill every 3 matches to keep feedback anonymous
            if feedback_count % 3 == 0:
                if skill:
                    skill = skill[0]
                    skill.calculate()
                    num_updates += 1
                else:
                    new_skill = Skill.objects.create(player=player,
                                                     sport=sport)
                    new_skill.calculate()
                    num_updates += 1

        self.stdout.write("{} Skills updated".format(num_updates))
