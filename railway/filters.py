from django_filters import rest_framework as filters


class TrainTypeFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Type name"
    )


class TrainFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Train name"
    )


class StationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Station name"
    )


class RouteFilterSet(filters.FilterSet):
    source = filters.CharFilter(
        field_name="source__name",
        lookup_expr="icontains",
        label="Source station",
    )
    destination = filters.CharFilter(
        field_name="destination__name",
        lookup_expr="icontains",
        label="Destination station",
    )


class JourneyFilterSet(filters.FilterSet):
    source = filters.CharFilter(
        field_name="route__source__name",
        lookup_expr="icontains",
        label="Source station",
    )
    destination = filters.CharFilter(
        field_name="route__destination__name",
        lookup_expr="icontains",
        label="Destination station",
    )
    train = filters.CharFilter(
        field_name="train__name",
        lookup_expr="icontains",
        label="Train name",
    )
    departure_date = filters.DateFilter(
        field_name="departure_time",
        lookup_expr="date",
        label="Departure date",
    )
    departure_range = filters.DateFromToRangeFilter(
        field_name="departure_time",
        label="Departure date range"
    )
    arrival = filters.DateFilter(
        field_name="arrival_time",
        lookup_expr="date",
        label="Arrival date"
    )
    arrival_range = filters.DateFromToRangeFilter(
        field_name="arrival_time",
        label="Arrival date range"
    )


class OrderFilterSet(filters.FilterSet):
    created_at = filters.DateTimeFilter(
        field_name="created_at",
        label="Created at"
    )
    created_range = filters.DateRangeFilter(
        field_name="created_at",
        label="Created at range"
    )


class CrewFilterSet(filters.FilterSet):
    first_name = filters.CharFilter(
        field_name="first_name",
        lookup_expr="icontains",
        label="First name",
    )
    last_name = filters.CharFilter(
        field_name="last_name",
        lookup_expr="icontains",
        label="Last name",
    )
