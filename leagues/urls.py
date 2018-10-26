from django.urls import path

from . import views

app_name = 'leagues'
urlpatterns = [
    path('', views.index, name='index'),
    path('modern/', views.modern, name='modern'),
    path('legacy/', views.legacy, name='legacy'),
]
