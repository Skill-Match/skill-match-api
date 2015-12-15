from datetime import timedelta, datetime
from django.core.management import BaseCommand
from matchup.models import Feedback, Skill


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        one_hour = timedelta(hours=1)
        new_feedbacks = Feedback.objects.filter(created_at__gt=
                                                (datetime.now() - one_hour))

        for feedback in new_feedbacks:
            player = feedback.player
            sport = feedback.match.sport
            feedback_count = Feedback.objects.filter(match__sport=sport).\
                filter(player=player).count()
            skill = Skill.objects.filter(player=player).filter(sport=sport)

            #Update Skill every 3 matches to keep feedback anonymous
            num_updates = 0
            if feedback_count % 3 == 0:
                if skill:
                    skill = skill[0]
                    feedbacks = Feedback.objects.filter(match__sport=sport).\
                        filter(player=player)
                    skill_total = 0
                    sportsmanship_total = 0
                    count = 0
                    for feedback in feedbacks:
                        skill_total += feedback.skill
                        sportsmanship_total += feedback.sportsmanship
                        count += 1
                    skill.skill = skill_total / count
                    skill.sportsmanship = sportsmanship_total / count
                    skill.num_feedbacks = count
                    skill.save()
                    num_updates += 1
                else:
                    new_skill = Skill.objects.create(player=player, sport=sport)
                    feedbacks = Feedback.objects.filter(match__sport=sport).\
                        filter(player=player)
                    skill_total = 0
                    sportsmanship_total = 0
                    count = 0
                    for feedback in feedbacks:
                        skill_total += feedback.skill
                        sportsmanship_total += feedback.sportsmanship
                        count += 1
                    new_skill.skill = skill_total / count
                    new_skill.sportsmanship = sportsmanship_total / count
                    new_skill.num_feedbacks = count
                    new_skill.save()
                    num_updates += 1

        self.stdout.write("{} Skills updated".format(num_updates))
