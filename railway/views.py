from django.db.models import Prefetch, F, Count
from rest_framework import viewsets

from railway.models import (
    TrainType,
    Train,
    Station,
    Route,
    Journey,
    Order,
    Crew, Ticket,
)
from railway.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    CrewSerializer,
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all().select_related("train_type")
    serializer_class = TrainSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (Journey.objects.all()
    .prefetch_related("crew")
    .select_related("route__source", "route__destination")
    .select_related("train__train_type")
    .annotate(
        tickets_available=F("train__cargo_num")
                          * F("train__places_in_cargo")
                          - Count("tickets")
    )
    )
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (Order.objects.filter(user=self.request.user)
        .prefetch_related(
            Prefetch(
                "tickets",
                queryset=Ticket.objects.select_related(
                    "journey__train",
                    "journey__route__source",
                    "journey__route__destination",
                ).prefetch_related("journey__crew")
            )
        )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
