"""URL configuration for diagram app."""
from django.urls import path
from . import views

app_name = 'diagram'

urlpatterns = [
    path('', views.index, name='index'),
    path('load-schema/', views.load_schema, name='load_schema'),
    path('toggle-table/', views.toggle_table, name='toggle_table'),
    path('toggle-column/', views.toggle_column, name='toggle_column'),
    path('generate/', views.generate_diagram, name='generate_diagram'),
    path('download/', views.download_diagram, name='download_diagram'),
]
