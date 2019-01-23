from django.urls import path, include

from . import views

app_name = 'leagues'
urlpatterns = [
    path('', views.index, name='index'),
    path('modern', views.modern, name='modern'),
    path('legacy', views.legacy, name='legacy'),
    path('cedh', views.cedh, name='cedh'),
    path('user/<int:pk>/', views.user_details, name='stats'),
    path('user/<int:pk>/<int:event>', views.event_details, name='event'),
    path('uploads', views.uploads, name='uploads'),
    path('upload-cedh', views.cedh_upload, name='cedh_upload')
]
