from django.urls import path
from . import views

urlpatterns =[
    path('showall/', views.showall, name='showallProduct'),
    path('create/', views.create, name='createProduct'),
    path('delete/<str:product_id>/', views.delete, name='deleteProduct'),
    path('update/<str:product_id>/', views.update, name='updateProduct'),

]