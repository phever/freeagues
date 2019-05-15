from django.urls import path, include

from . import views

app_name = 'leagues'
urlpatterns = [
    path('', views.index_view, name='index_view'),
    path('modern', views.modern_view, name='modern_view'),
    path('old-events/modern/<int:pk>', views.old_modern_view, name='old_modern_view'),
    path('legacy', views.legacy_view, name='legacy_view'),
    path('old-events/legacy/<int:pk>', views.old_legacy_view, name='old_legacy_view'),
    path('standard', views.standard_view, name='standard_view'),
    path('old-events/standard/<int:pk>', views.old_standard_view, name='old_standard_view'),
    path('cedh', views.cedh_view, name='cedh_view'),
    path('old-events/cedh/<int:pk>', views.old_cedh_view, name='old_cedh_view'),
    path('old-leagues', views.old_league_view, name='old_league_view'),
    path('player/<int:pk>/', views.player_details_view, name='stats'),
    path('player/<int:pk>/result/<int:event>', views.sixty_personal_event_view, name='60_card_personal_event'),
    path('event/<int:pk>', views.full_event_view, name='event'),
    path('uploads', views.uploads_view, name='uploads_view'),
    path('upload-cedh', views.cedh_upload_view, name='cedh_upload_view'),
    path('upload-player', views.player_upload_view, name='player_upload_view'),
    path('upload-new-league', views.new_league_upload_view, name='new_league_upload_view')
]
