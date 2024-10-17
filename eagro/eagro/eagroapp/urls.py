from django.urls import path
from . import views

urlpatterns = [
	path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('crop',views.crop_recommend,name='crop'),
    path('crop-recommendation/',views.crop_prediction,name='crop_prediction'),
    path('fertilizer',views.fertilizer_recommendation,name='fertilizer'),
    path('fertilizer-recommendation/',views.fert_recommend,name='fert_recommend'),
    path('Crop-disease/',views.disease,name='disease'),
    path('Crop-disease-prediction/',views.disease_prediction,name='disease_prediction'),
	path('user-login/', views.userlogin, name='userlogin'),
    path('user-signup/', views.usersignup, name='usersignup'),
	path('logout/', views.logout_view, name='logout'),
]
