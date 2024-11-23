from django.urls import path
from . import views

urlpatterns = [
    path('', views.fbapp, name="fbapp"),
    path("nav/", views.searchnav, name="searchnav"),
    path("dash/", views.dash, name="dash"),
    path("profile/", views.profile, name="profile"),
    path("statistics/", views.statistics, name="statistics"),
    path("stat/", views.stat, name="stat"),
    path("news/", views.news, name="news"),
    path("article/", views.article, name="article"),
    path("makeart/", views.makeart, name="makeart"),
    path("livechat/", views.livechat, name="livechat"),
    path("<str:room_name>/", views.room, name="room"),
]
