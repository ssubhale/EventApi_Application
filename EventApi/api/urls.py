from django.urls import path
from api.views import *


urlpatterns = [
    path('signup_user/',signup_user, name='signup_user'),
    path('sign_in_user/',sign_in_user, name='sign_in_user'),
    path('create_event/',create_event, name='create_event'),
    path('get_events/', get_events, name='get_events'),
    path('events/<int:id>/purchase/', purchase_tickets, name='purchase_tickets'),
    
]

