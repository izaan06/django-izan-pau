from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Vista principal: renderitza la plantilla home.html
def home(request):
    return render(request, "home.html")

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutes de la teva app d’usuaris
    path("users/", include(("users.urls", "users"), namespace="users")),

    # Rutes de l'app d'esdeveniments
    path("events/", include(("events.urls", "events"), namespace="events")),
    
    # Pàgina d'inici
    path("", home, name="home"),
    
    path('chat/', include('chat.urls')),
]

# Servir arxius multimèdia en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
