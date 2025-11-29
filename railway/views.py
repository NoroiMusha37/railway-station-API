from django.db.models import Prefetch, F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    TrainImageSerializer,
    StationSerializer,
    StationImageSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    CrewSerializer,
    CrewImageSerializer,
)
from railway.filters import (
    TrainTypeFilterSet,
    TrainFilterSet,
    StationFilterSet,
    RouteFilterSet,
    JourneyFilterSet,
    OrderFilterSet,
    CrewFilterSet,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by train type name"
        ),
    ]
)
class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    filterset_class = TrainTypeFilterSet


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by train name"
        ),
    ]
)
class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all().select_related("train_type")
    serializer_class = TrainSerializer
    filterset_class = TrainFilterSet

    def get_serializer_class(self):
        if self.action == "upload_image":
            return TrainImageSerializer
        return TrainSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by station name"
        ),
    ]
)
class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filterset_class = StationFilterSet

    def get_serializer_class(self):
        if self.action == "upload_image":
            return StationImageSerializer
        return StationSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        station = self.get_object()
        serializer = self.get_serializer(station, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="source",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by source station name."
        ),
        OpenApiParameter(
            name="destination",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by destination station name."
        ),
    ]
)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    filterset_class = RouteFilterSet

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="source",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by source station name."
        ),
        OpenApiParameter(
            name="destination",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by destination station name."
        ),
        OpenApiParameter(
            name="train",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by train name."
        ),
        OpenApiParameter(
            name="departure_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Journeys departing on a given date."
        ),
        OpenApiParameter(
            name="departure_range_after",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Start of the departure date range."
        ),
        OpenApiParameter(
            name="departure_range_before",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="End of the departure date range."
        ),
        OpenApiParameter(
            name="arrival",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Journeys arriving on a given date."
        ),
        OpenApiParameter(
            name="arrival_range_after",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Start of arrival date range."
        ),
        OpenApiParameter(
            name="arrival_range_before",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="End of arrival date range."
        ),
    ]
)
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
    filterset_class = JourneyFilterSet

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="created_at",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            description="Filter orders created at the given timestamp."
        ),
        OpenApiParameter(
            name="created_range_after",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Start of creation date range."
        ),
        OpenApiParameter(
            name="created_range_before",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="End of creation date range."
        ),
    ]
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_class = OrderFilterSet
    permission_classes = (IsAuthenticated,)

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


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="first_name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter crew by first name."
        ),
        OpenApiParameter(
            name="last_name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter crew by last name."
        ),
    ]
)
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    filterset_class = CrewFilterSet

    def get_serializer_class(self):
        if self.action == "upload_image":
            return CrewImageSerializer
        return CrewSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        crew = self.get_object()
        serializer = self.get_serializer(crew, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
