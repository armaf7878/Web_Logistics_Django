from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('showall/', views.showall, name='showall'),
    path('update/<str:user_id>/', views.update, name='update'),
    path('delete/<str:user_id>/', views.delete, name='delete'),
]
