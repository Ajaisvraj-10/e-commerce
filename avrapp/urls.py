from django.urls import path
from avrapp import views

urlpatterns = [
      path('',views.home,name='homr')
       
]
