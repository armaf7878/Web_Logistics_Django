"""
URL configuration for logistic_nhom03 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# === BẮT ĐẦU THÊM MỚI: Import views của app dashboard ===
from dashboard import views as dashboard_views
# === KẾT THÚC THÊM MỚI ===

urlpatterns = [
    # === BẮT ĐẦU THÊM MỚI: Thêm đường dẫn gốc (rỗng) trỏ đến dashboard ===
    path('', dashboard_views.dashboard, name='root_dashboard'),
    # === KẾT THÚC THÊM MỚI ===
    
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('exports/', include('exports.urls')),
    path('deliver/', include('delivery.urls')),
    path('trackings/', include('trackings.urls'))
]