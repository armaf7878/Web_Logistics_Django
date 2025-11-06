from django.urls import path, include
from . import views
urlpatterns=[
    path('processing/<str:export_id>/', views.processing, name='processing'),
    path('update_location/', views.update_location, name='update_location'),
    path('delivering/complete/', views.complete, name='deliveringComplete'),
    path('delivering/', views.delivering, name='delivering'),
    path('', views.showall, name='deliver') 
]

