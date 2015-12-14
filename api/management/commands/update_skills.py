from django.core.management import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
        
    def handle(self, *args, **options):
        Feedback.objects.filter(created_at__lt=)







# @property
# def skill(self):
#     """Return average skill over feedback set"""
#     total = 0
#     count = 0
#     if self.user.players.all():
#         for match in self.user.players.all():
#             feedbacks = match.feedback_set.filter(player=self.user)
#             if feedbacks:
#                 total += feedbacks[0].skill
#                 count += 1
#                 return round(total / count, 2)
#
#     return None