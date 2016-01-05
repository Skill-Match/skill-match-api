from django.contrib import admin
from users.models import Profile, Skill


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'age', 'avatar')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'sport', 'skill', 'sportsmanship',
                    'num_feedbacks')