from django.urls import path
from . import views

app_name = 'arsip'

urlpatterns = [
    path('', views.arsip_list, name='arsip-list'),
    path('buat-arsip/', views.create_arsip_view, name='arsip-register'),
    path('arsip-detail/<id>/', views.arsip_detail, name='arsip-detail'),
    path('arsip/<int:id>/request-tarik/', views.request_tarik, name='request-tarik'),
    path('arsip/<int:id>/request-ganti/', views.request_ganti, name='request-ganti'),
    path('arsip/<int:id>/posting', views.approve_request, name='posting-arsip'),
]