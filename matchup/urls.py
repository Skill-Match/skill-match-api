from django.conf.urls import url
from matchup import views as matchup_views
from matchup.views import  ListCreateMatches, ListParks, \
    CreateFeedbacks, DetailPark, DetailUpdateMatch, \
    DetailUpdateFeedback,   \
    JoinMatch, DeclineMatch, ConfirmMatch,  \
    CreateCourts, LeaveMatch, ChallengeCreateMatch, DetailUpdateCourt
from users.views import ListUsers, CreateUser, DetailUpdateUser, \
    ObtainAuthToken

urlpatterns = (
    url(r'^users/$', ListUsers.as_view(), name='api_list_users'),
    url(r'^users/create/$', CreateUser.as_view(), name='api_create_user'),
    url(r'^users/(?P<pk>\d+)/$', DetailUpdateUser.as_view(),
        name='api_detail_update_user'),
    url(r'^api-token-auth/$', ObtainAuthToken.as_view(),
        name='api_obtain_auth_token'),
    url(r'^parks/$', ListParks.as_view(), name='api_list_parks'),
    url(r'^parks/(?P<pk>\d+)', DetailPark.as_view(), name='api_park_detail'),
    url(r'^matches/$', ListCreateMatches.as_view(),
        name='api_list_create_matches'),
    url(r'^matches/challenge/$', ChallengeCreateMatch.as_view(),
        name='api_challenge'),
    url(r'^matches/(?P<pk>\d+)/$', DetailUpdateMatch.as_view(),
        name='api_detail_update_match'),
    url(r'^matches/(?P<pk>\d+)/join/$', JoinMatch.as_view(),
        name='api_join_match'),
    url(r'^matches/(?P<pk>\d+)/leave/$', LeaveMatch.as_view(),
        name='api_leave_match'),
    url(r'^matches/(?P<pk>\d+)/confirm/$', ConfirmMatch.as_view(),
        name='api_confirm_match'),
    url(r'^matches/(?P<pk>\d+)/decline/$', DeclineMatch.as_view(),
        name='api_decline_match'),
    url(r'^courts/$', CreateCourts.as_view(), name='api_create_courts'),
    url(r'^courts/(?P<pk>\d+)/$', DetailUpdateCourt.as_view(),
        name='api_detail_update_court'),
    url(r'^feedbacks/(?P<pk>\d+)', DetailUpdateFeedback.as_view(),
        name='api_detail_update_feedback'),
    url(r'^feedbacks/create/$', CreateFeedbacks.as_view(),
        name='api_create_feedback'),
)
