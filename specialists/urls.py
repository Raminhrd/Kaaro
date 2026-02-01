from django.urls import path
from specialists.views import SpecialistRequestMeView

urlpatterns = [
    path("request/", SpecialistRequestMeView.as_view(), name="specialist-request-me"),
]
