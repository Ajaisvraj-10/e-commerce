from django.urls import path
from avrauth import views

urlpatterns = [
      path('signup/',views.signup,name='signup'),
      path('login/',views.user_login,name='login'),
      path('logout/',views.user_logout,name='logout'),
      path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
      path('request_password/',views.ResetEmailView.as_view(),name='request_password'),
      path('set-new-password/<uidb64>/<token>',views.SetNewPasswordView.as_view(),name='set-new-password'),
]