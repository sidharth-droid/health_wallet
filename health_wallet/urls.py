from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (
    register,
    profile,
    add_medical_history,
    edit_medical_history,
    delete_medical_history,
    add_prescription,
    edit_prescription,
    delete_prescription,
    view_medical_history,
    view_record_details,
    dashboard,
    prescription_list,
    manage_permissions,
    view_record_permissions
)

urlpatterns = [
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('profile/', profile, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    # Medical History URLs
    path('manage_permissions/<int:record_id>/', manage_permissions, name='manage_permissions'),
    path('medical_history/add/', add_medical_history, name='add_medical_history'),
    path('medical_history/view/', view_medical_history, name='view_medical_history'),
    path('medical_history/edit/<int:pk>/', edit_medical_history, name='edit_medical_history'),
    path('medical_history/delete/<int:record_id>/', delete_medical_history, name='delete_medical_history'),
    path('medical_history/details/<int:record_id>/', view_record_details, name='view_record_details'),
    path('view_record_permissions/<int:record_id>/',view_record_permissions, name='view_record_permissions'),


    # Prescription URLs
    path('prescription/add/', add_prescription, name='add_prescription'),
    path('prescription/edit/<int:pk>/', edit_prescription, name='edit_prescription'),
    path('prescription/delete/<int:pk>/', delete_prescription, name='delete_prescription'),
    path('prescription/list/', prescription_list, name='prescription_list'),  
    

]
