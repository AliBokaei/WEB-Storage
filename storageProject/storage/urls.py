from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('download/<int:file_id>/', views.download_view, name='download_file'),
    path('delete/<int:file_id>/', views.delete_view, name='delete_file'),
    # path('search/', views.search_view, name='search_file'),
    path('search/', views.search_view, name='search_file'),
    path('save_selected_users/', views.save_selected_users, name='save_selected_users'),]
