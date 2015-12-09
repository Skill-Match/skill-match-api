from django.contrib import admin
from matchup.models import Feedback, Match, Park


@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'park', 'sport',
                    'skill_level', 'date', 'time', 'is_open', 'is_completed',
                    'is_confirmed')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'player', 'match', 'skill',
                    'sportsmanship', 'availability')


# @admin.register(WishList)
# class WishListAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'title', 'expiration', 'is_expired',
#                     'created_at')
#
# @admin.register(Item)
# class ItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'wish_list', 'title', 'description', 'price',
#                     'source_url', 'is_funded', 'image_url',
#                     'is_closed', 'created_at')
#
# @admin.register(Pledge)
# class PledgeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'item', 'amount', 'charge_id',
#                     'is_refunded', 'pledged_at')