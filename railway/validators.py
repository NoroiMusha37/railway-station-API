from django.utils import timezone
from rest_framework import serializers
from railway.models import Journey


class RouteValidationMixin:
    def validate(self, attrs):
        source = attrs.get("source")
        destination = attrs.get("destination")

        # source and destination stations should be different
        if source == destination:
            raise serializers.ValidationError(
                {"destination": "source and destination cannot be the same"})


class JourneyValidationMixin:
    def validate(self, attrs):
        departure = attrs.get("departure_time")
        arrival = attrs.get("arrival_time")
        train = attrs.get("train")
        crew = attrs.get("crew")
        instance_id = getattr(self.instance, "id", None)

        # departure time should be <= arrival time
        if departure > arrival:
            raise serializers.ValidationError(
                {"arrival_time": "departure must be earlier than arrival"}
            )

        # departure time should be > than now
        if departure < timezone.now():
            raise serializers.ValidationError(
                {"departure_time": "departure cannot be in past"}
            )

        # train shouldn't be on another journey at [departure_time; arrival_time]
        busy_train = Journey.objects.filter(
            train=train,
            departure_time__lte=arrival,
            arrival_time__gte=departure,
        )
        if instance_id:
            busy_train = busy_train.exclude(pk=instance_id)

        if busy_train.exists():
            raise serializers.ValidationError(
                {"train": f"the train is busy in {departure} - {arrival}"}
            )

        # any crew member shouldn't be on another journey at [departure_time; arrival_time]
        busy_crew = Journey.objects.filter(
            crew__in=crew,
            departure_time__lte=arrival,
            arrival_time__gte=departure,
        )
        if instance_id:
            busy_crew = busy_crew.exclude(pk=instance_id)

        if busy_crew.exists():
            raise serializers.ValidationError(
                {"crew": f"some crew members are busy in "
                         f"{departure} - {arrival}"}
            )

        return attrs


class TicketValidationMixin:
    def validate(self, attrs):
        cargo = attrs["cargo"]
        seat = attrs["seat"]
        journey = attrs["journey"]
        train = journey.train

        # booked cargo should be in range [1; train_cargos]
        if not (1 <= cargo <= train.cargo_num):
            raise serializers.ValidationError(
                {"cargo": f"cargo must be in range [1, {train.cargo_num}]"}
            )

        # booked seat should be in range [1; cargo_seats]
        if not (1 <= seat <= train.places_in_cargo):
            raise serializers.ValidationError(
                {"seat": f"seat must be in range [1, {train.places_in_cargo}]"}
            )

        return attrs
