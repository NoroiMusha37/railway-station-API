from django.db import transaction
from rest_framework import serializers

from railway.models import (
    TrainType,
    Train,
    Station,
    Route,
    Journey,
    Order,
    Ticket,
    Crew,
)
from railway.validators import (
    RouteValidationMixin,
    JourneyValidationMixin,
    TicketValidationMixin,
)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.SlugRelatedField(
        slug_field="name", queryset=TrainType.objects.all()
    )

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "total_places",
            "train_type",
            "image",
        )


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "image")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude", "image")


class StationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "image")


class RouteSerializer(RouteValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(
        source="destination.name", read_only=True
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "image")


class CrewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "image")


class JourneySerializer(JourneyValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "journey_time",
            "crew",
        )


class JourneyListSerializer(JourneySerializer):
    route = serializers.CharField(source="route.full_route", read_only=True)
    train = serializers.CharField(source="train.name", read_only=True)
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name",
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "journey_time",
            "crew",
            "tickets_available",
        )


class JourneyDetailSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    taken_places = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "journey_time",
            "crew",
            "taken_places",
        )

    @staticmethod
    def get_taken_places(obj):
        return list(obj.tickets.values("cargo", "seat"))


class TicketSerializer(serializers.ModelSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class TicketCreateSerializer(
    TicketValidationMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat", "journey")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(
        many=True, read_only=False, allow_empty=False
    )

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
