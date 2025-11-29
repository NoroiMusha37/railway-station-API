from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from railway.views import (
    TrainTypeViewSet,
    TrainViewSet,
    StationViewSet,
    RouteViewSet,
    JourneyViewSet,
    OrderViewSet, CrewViewSet,
)


app_name = "railway"
router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)
router.register("crew", CrewViewSet)
urlpatterns = [
    path("", include(router.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
