from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include(("users.urls"))),
    path('services/', include("services.urls")),
    path('tasks/', include("tasks.urls")),
    path("specialists/", include("specialists.urls")),

]
