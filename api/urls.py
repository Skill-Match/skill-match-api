from api.views import CreateUser, ListUsers, ListCreateMatches, ListCreateParks, \
    ListFeedbacks, CreateFeedbacks, DetailPark, DetailUpdateMatch, \
    DetailFeedback
from django.conf.urls import url
from rest_framework.authtoken import views

urlpatterns = [
    url(r'^users/$', ListUsers.as_view(), name='api_list_users'),
    url(r'^users/create/$', CreateUser.as_view(), name='api_create_user'),
    url(r'^api-token-auth/$', views.obtain_auth_token),
    url(r'^matches/$', ListCreateMatches.as_view(),
        name='api_list_create_matches'),
    url(r'^matches/(?P<pk>\d+)', DetailUpdateMatch.as_view(),
        name='api_detail_update_matc'),
    url(r'^parks/$', ListCreateParks.as_view(), name='api_list_create_parks'),
    url(r'^parks/(?P<pk>\d+)', DetailPark.as_view(), name='api_park_detail'),
    url(r'^feedbacks/$', ListFeedbacks.as_view(), name='api_list_feebacks'),
    url(r'^feedbacks/(?P<pk>\d+)', DetailFeedback.as_view(),
        name='api_detail_feedback'),
    url(r'^feedbacks/create/$', CreateFeedbacks.as_view(),
        name='api_create_feeback'),
]
