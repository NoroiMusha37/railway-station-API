from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


class TrainType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField(validators=[MinValueValidator(1)])
    places_in_cargo = models.IntegerField(validators=[MinValueValidator(1)])
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains",
    )

    @property
    def total_places(self):
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return f"{self.name} ({self.places_in_cargo})"


class Station(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = ("latitude", "longitude")

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes_s",
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes_d",
    )
    distance = models.IntegerField(validators=[MinValueValidator(1)])

    @property
    def full_route(self):
        return f"{self.source.name} - {self.destination.name}"

    def __str__(self):
        return f"{self.full_route} ({self.distance})"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys",
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    @property
    def journey_time(self):
        return str(self.arrival_time - self.departure_time)

    def __str__(self):
        return (f"{self.train.name} - {self.route.__str__()} "
                f"({self.departure_time}, {self.arrival_time})")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    class Meta:
        unique_together = ("cargo", "seat", "journey")

    def __str__(self):
        return f"{self.seat}, {self.cargo}"
