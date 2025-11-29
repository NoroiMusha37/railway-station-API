from django.utils import timezone
from rest_framework import serializers
from railway.models import Journey


class RouteValidationMixin:
    def validate(self, attrs):
        source = attrs.get("source") or getattr(self.instance, "source", None)
        destination = attrs.get("destination") or getattr(
            self.instance, "destination", None
        )

        # source and destination stations should be different
        if source == destination:
            raise serializers.ValidationError(
                {"destination": "source and destination cannot be the same"}
            )

        return attrs


class JourneyValidationMixin:
    def validate(self, attrs):
        departure = attrs.get("departure_time") or getattr(
            self.instance, "departure_time", None
        )
        arrival = attrs.get("arrival_time") or getattr(
            self.instance, "arrival_time", None
        )
        train = attrs.get("train") or getattr(self.instance, "train", None)
        crew = attrs.get("crew")
        if crew is None:
            crew = getattr(self.instance, "crew").values_list("id", flat=True)
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

        # train shouldn't be on another journey
        # at [departure_time; arrival_time]
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

        # any crew member shouldn't be on another journey
        # at [departure_time; arrival_time]
        busy_crew = Journey.objects.filter(
            crew__in=crew,
            departure_time__lte=arrival,
            arrival_time__gte=departure,
        ).distinct()

        if instance_id:
            busy_crew = busy_crew.exclude(pk=instance_id)

        if busy_crew.exists():
            raise serializers.ValidationError(
                {"crew": f"some crew members are busy "
                         f"in {departure} - {arrival}"}
            )

        return attrs


class TicketValidationMixin:
    def validate(self, attrs):
        cargo = attrs.get("cargo") or getattr(self.instance, "cargo", None)
        if cargo is None:
            cargo = getattr(self.instance, "cargo", None)
        seat = attrs.get("seat") or getattr(self.instance, "seat", None)
        if seat is None:
            seat = getattr(self.instance, "seat", None)
        journey = (attrs.get("journey")
                   or getattr(self.instance, "journey", None))
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
