from django.urls import path
from . import views

# Namespace per l'app events
app_name = 'events'

urlpatterns = [
    # Llistat d'esdeveniments
    path('', views.event_list_view, name='event_list'),

    # Crear un nou esdeveniment
    path('create/', views.event_create_view, name='event_create'),

    # Detall d'un esdeveniment (per pk)
    path('<int:pk>/', views.event_detail_view, name='event_detail'),

    # Editar un esdeveniment existent
    path('<int:pk>/edit/', views.event_update_view, name='event_update'),

    # Eliminar un esdeveniment
    path('<int:pk>/delete/', views.event_delete_view, name='event_delete'),

    # Llistat dels esdeveniments de l'usuari actual
    path('my-events/', views.my_events_view, name='my_events'),

    # Filtrar esdeveniments per categoria
    path('category/<str:category>/', views.events_by_category_view, name='events_by_category'),
]
