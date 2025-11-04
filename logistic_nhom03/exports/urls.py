from django.urls import path, include
from . import views

urlpatterns = [
    path('showall/', views.showall, name='showallExports'),
    path('create/', views.create, name='createlExport'),
    path('create/step-2/', views.chooseproduct, name='createlExport2'),
    path('import/', views.imports, name='import'),
    path('detail/<str:export_id>/', views.detail, name='detailExport'),
]