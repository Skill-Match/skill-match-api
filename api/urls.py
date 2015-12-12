from api.views import CreateUser, ListUsers, ListCreateMatches, ListParks, \
    ListFeedbacks, CreateFeedbacks, DetailPark, DetailUpdateMatch, \
    DetailFeedback, UpdateMatch, DetailUpdateUser, CreatePark
from django.conf.urls import url
from rest_framework.authtoken import views

urlpatterns = [
    url(r'^users/$', ListUsers.as_view(), name='api_list_users'),
    url(r'^users/create/$', CreateUser.as_view(), name='api_create_user'),
    url(r'^users/(?P<pk>\d+)/', DetailUpdateUser.as_view(),
        name='api_detail_update_user'),
    url(r'^api-token-auth/$', views.obtain_auth_token),
    url(r'^matches/$', ListCreateMatches.as_view(),
        name='api_list_create_matches'),
    url(r'^matches/(?P<pk>\d+)/$', DetailUpdateMatch.as_view(),
        name='api_detail_update_match'),
    url(r'^matches/(?P<pk>\d+)/signup/$', UpdateMatch.as_view(),
        name='api_update_match'),
    url(r'^parks/$', ListParks.as_view(), name='api_list_parks'),
    url(r'^parks/create/$', CreatePark.as_view(), name='api_create_park'),
    url(r'^parks/(?P<pk>\d+)', DetailPark.as_view(), name='api_park_detail'),
    url(r'^feedbacks/$', ListFeedbacks.as_view(), name='api_list_feebacks'),
    url(r'^feedbacks/(?P<pk>\d+)', DetailFeedback.as_view(),
        name='api_detail_feedback'),
    url(r'^feedbacks/create/$', CreateFeedbacks.as_view(),
        name='api_create_feeback'),
    url(r'^yelp/$', 'api.views.hello_world')
]
