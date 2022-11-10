from django.urls import path
from django.contrib import admin

from . import views

app_name = 'newsbag_app'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('create', views.addNewLibrary, name='create'),
    path('<category>', views.landing, name='landing'),
    path('signup/<id>', views.signup, name='signup'),
    path('login/<id>', views.loginUser, name='login'),
    path('collection/<id>', views.collection, name='collection'),
    path('logout/<id>', views.logoutUser, name='logout'),
    path('library/<id>', views.visitLibrary, name='library'),
    path('compare/<lid>/<aid>', views.compare, name='compare'),
]
