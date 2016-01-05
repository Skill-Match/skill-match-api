from api.calculations import calculate_skills
from django.core.management import BaseCommand
from matchup.models import Feedback
from users.models import Skill


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        feedbacks = Feedback.objects.all()

        num_updates = 0
        for feedback in feedbacks:
            player = feedback.player
            sport = feedback.match.sport
            skill = Skill.objects.filter(player=player).filter(sport=sport)

            if skill:
                skill = skill[0]
                calculate_skills(skill, sport)
            else:
                new_skill = Skill.objects.create(player=player, sport=sport)
                calculate_skills(new_skill, sport)

        self.stdout.write("Skills updated successfully".format(num_updates))