from django.urls import path

from .views import (
    livestream_view,
    cctv
)

app_name = 'cctv'

urlpatterns = [
    path('cameras/<str:cam>/', livestream_view, name='cameras'),
    path('', cctv, name='cctv'),
]
