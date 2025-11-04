from django.urls import path, include
from . import views
urlpatterns=[
    path('processing/<str:export_id>/', views.processing, name='processing'),
    
    path('', views.showall, name='deliver')
    
]

