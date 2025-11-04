from django.urls import path
from . import views

urlpatterns = [
    path('<str:tracking_id>/', views.detail, name='deatailTracking'),
    path('', views.showall, name='showallTracking'),
 ]