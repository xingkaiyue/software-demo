
from django.urls import path
from .register_views import Register
from . login_views import Login

urlpatterns = [
    path('register/',Register.as_view(),name='register'),
    path('login/',Login.as_view(),name='login'),

]