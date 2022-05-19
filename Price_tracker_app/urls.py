from django.conf.urls import url
from django.urls import path

from Price_tracker_app import views

app_name = 'price_tracker'
urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('sign_up/', views.signup_view, name='sign up'),
    path('log_in/', views.login_view, name='log in'),
    path('logout/', views.logout_view, name = 'logout'),
    path('history/', views.history, name = 'history'),
    path('feedback/', views.feedback, name = 'feedback')
]