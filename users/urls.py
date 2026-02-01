from django.urls import path, include
from users import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('signup/', views.SignUpView.as_view()),

    path('otp/request/', views.OTPRequestView.as_view()),
    path('otp/login/', views.OTPLoginView.as_view()),

    path('info/', views.UserInfoView.as_view()),
]