from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('ucuslar', views.UcuslarViewset, basename="ucuslar")
router.register('airport', views.HavaalaniViewset, basename="airport")

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('', include(router.urls)),
]