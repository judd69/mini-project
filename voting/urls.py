"""SecureVote — URL patterns for the voting engine."""
from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Elections
    path('elections/', views.election_list, name='election_list'),
    path('elections/<int:election_id>/vote/', views.vote_view, name='vote'),
    path('elections/<int:election_id>/cast/', views.cast_vote, name='cast_vote'),
    path('elections/<int:election_id>/confirmation/', views.confirmation_view, name='confirmation'),
    path('elections/<int:election_id>/results/', views.results_view, name='results'),
]
