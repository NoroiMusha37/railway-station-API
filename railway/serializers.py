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
        read_only=True,
        slug_field="name",
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
        )


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(RouteValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class JourneySerializer(JourneyValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyListSerializer(JourneySerializer):
    route = serializers.SlugRelatedField(
        read_only=True, slug_field="full_route"
    )
    train = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name",
    )


class JourneyDetailSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    journey = JourneyListSerializer(many=False, read_only=False)

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class TicketCreateSerializer(TicketValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat", "journey")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, read_only=False, allow_empty=False)

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
    tickets = TicketSerializer(many=True, read_only=False)
