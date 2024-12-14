from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.fbapp, name="fbapp"),
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("signupto/", views.signupto, name="signupto"),
    path("signinto/", views.signinto, name="signinto"),
    path("signout/", views.signout, name="signout"),
    path("tankbar/", views.tankbar, name="tankbar"),
    path("bheader/", views.bheader, name="bheader"),
    path("dash/", views.dash, name="dash"),
    path("profile/", views.profile, name="profile"),
    path("teamprofile/", views.teamprofile, name="teamprofile"),
    path("teamchoice/<str:tid>/", views.teamchoice, name="teamchoice"),
    path("playerprofile/", views.playerprofile, name="playerprofile"),
    path("playerchoice/<str:playerID>/", views.playerchoice, name="playerchoice"),
    path("stat/", views.stat, name="stat"),
    path("article/", views.article, name="article"),
    path("articles/", views.articles, name="articles"),
    path("makeart/", views.makeart, name="makeart"),
    path("games/", views.games, name="games"),
    path("gameschat/", views.gameschat, name="gameschat"),
    path("playbyplay/<str:gameID>/",views.playbyplay, name="playbyplay"),
    path("room/<str:gameID/", views.room, name="room"),
    path("message/", views.message, name="message"),
    path("streamchat/", views.streamchat, name="streamchat"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
