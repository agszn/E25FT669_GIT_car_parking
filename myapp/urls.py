from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    
    path('3d/', views.parking_3d_view, name='parking_3d'),
    path('api/slots/', views.parking_slots_json, name='parking_slots_json'),
    path('api/slot/update/', views.parking_slot_update_api, name='parking_slot_update_api'),
    
    path('parking_slots/', views.parking_slots_view, name='parking_slots'),
    
]
