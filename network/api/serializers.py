"""SatNOGS Network API serializers, django rest framework"""
#  pylint: disable=no-self-use
from __future__ import absolute_import, division

from collections import defaultdict

from future.builtins import round
from rest_framework import serializers

from network.base.db_api import DBConnectionError, get_transmitters_by_uuid_set
from network.base.models import Antenna, DemodData, Observation, Station, \
    Transmitter
from network.base.perms import UserNoPermissionError, \
    check_schedule_perms_per_station
from network.base.scheduling import create_new_observation
from network.base.stats import transmitter_stats_by_uuid
from network.base.validators import ObservationOverlapError, OutOfRangeError, \
    check_end_datetime, check_overlaps, check_start_datetime, \
    check_start_end_datetimes, check_transmitter_station_pairs


class DemodDataSerializer(serializers.ModelSerializer):
    """SatNOGS Network DemodData API Serializer"""
    class Meta:
        model = DemodData
        fields = ('payload_demod', )


class ObservationSerializer(serializers.ModelSerializer):
    """SatNOGS Network Observation API Serializer"""
    transmitter = serializers.SerializerMethodField()
    transmitter_updated = serializers.SerializerMethodField()
    norad_cat_id = serializers.SerializerMethodField()
    station_name = serializers.SerializerMethodField()
    station_lat = serializers.SerializerMethodField()
    station_lng = serializers.SerializerMethodField()
    station_alt = serializers.SerializerMethodField()
    demoddata = DemodDataSerializer(many=True)

    class Meta:
        model = Observation
        fields = (
            'id', 'start', 'end', 'ground_station', 'transmitter', 'norad_cat_id', 'payload',
            'waterfall', 'demoddata', 'station_name', 'station_lat', 'station_lng', 'station_alt',
            'vetted_status', 'archived', 'archive_url', 'client_version', 'client_metadata',
            'vetted_user', 'vetted_datetime', 'rise_azimuth', 'set_azimuth', 'max_altitude',
            'transmitter_uuid', 'transmitter_description', 'transmitter_type',
            'transmitter_uplink_low', 'transmitter_uplink_high', 'transmitter_uplink_drift',
            'transmitter_downlink_low', 'transmitter_downlink_high', 'transmitter_downlink_drift',
            'transmitter_mode', 'transmitter_invert', 'transmitter_baud', 'transmitter_updated',
            'tle'
        )
        read_only_fields = [
            'id', 'start', 'end', 'observation', 'ground_station', 'transmitter', 'norad_cat_id',
            'archived', 'archive_url', 'station_name', 'station_lat', 'station_lng', 'vetted_user',
            'station_alt', 'vetted_status', 'vetted_datetime', 'rise_azimuth', 'set_azimuth',
            'max_altitude', 'transmitter_uuid', 'transmitter_description', 'transmitter_type',
            'transmitter_uplink_low', 'transmitter_uplink_high', 'transmitter_uplink_drift',
            'transmitter_downlink_low', 'transmitter_downlink_high', 'transmitter_downlink_drift',
            'transmitter_mode', 'transmitter_invert', 'transmitter_baud', 'transmitter_created',
            'transmitter_updated', 'tle'
        ]

    def update(self, instance, validated_data):
        """Updates observation object with validated data"""
        validated_data.pop('demoddata')
        super(ObservationSerializer, self).update(instance, validated_data)
        return instance

    def get_transmitter(self, obj):
        """Returns Transmitter UUID"""
        try:
            return obj.transmitter_uuid
        except AttributeError:
            return ''

    def get_transmitter_updated(self, obj):
        """Returns Transmitter last update date"""
        try:
            return obj.transmitter_created
        except AttributeError:
            return ''

    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID"""
        return obj.satellite.norad_cat_id

    def get_station_name(self, obj):
        """Returns Station name"""
        try:
            return obj.ground_station.name
        except AttributeError:
            return None

    def get_station_lat(self, obj):
        """Returns Station latitude"""
        try:
            return obj.ground_station.lat
        except AttributeError:
            return None

    def get_station_lng(self, obj):
        """Returns Station longitude"""
        try:
            return obj.ground_station.lng
        except AttributeError:
            return None

    def get_station_alt(self, obj):
        """Returns Station elevation"""
        try:
            return obj.ground_station.alt
        except AttributeError:
            return None


class NewObservationListSerializer(serializers.ListSerializer):
    """SatNOGS Network New Observation API List Serializer"""
    transmitters = {}

    def validate(self, attrs):
        """Validates data from a list of new observations"""
        station_set = set()
        transmitter_uuid_set = set()
        transmitter_uuid_station_set = set()
        start_end_per_station = defaultdict(list)

        for observation in attrs:
            station = observation.get('ground_station')
            transmitter_uuid = observation.get('transmitter_uuid')

            station_set.add(station)
            transmitter_uuid_set.add(transmitter_uuid)
            transmitter_uuid_station_set.add((transmitter_uuid, station))
            start_end_per_station[int(station.id)].append(
                (observation.get('start'), observation.get('end'))
            )

        try:
            check_overlaps(start_end_per_station)
        except ObservationOverlapError as error:
            raise serializers.ValidationError(error, code='invalid')

        try:
            check_schedule_perms_per_station(self.context['request'].user, station_set)
        except UserNoPermissionError as error:
            raise serializers.ValidationError(error, code='forbidden')

        try:
            transmitters = get_transmitters_by_uuid_set(transmitter_uuid_set)
            self.transmitters = transmitters
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        except DBConnectionError as error:
            raise serializers.ValidationError(error)

        transmitter_station_list = [
            (transmitters[pair[0]], pair[1]) for pair in transmitter_uuid_station_set
        ]
        try:
            check_transmitter_station_pairs(transmitter_station_list)
        except OutOfRangeError as error:
            raise serializers.ValidationError(error, code='invalid')
        return attrs

    def create(self, validated_data):
        """Creates new observations from a list of new observations validated data"""
        new_observations = []
        for observation_data in validated_data:

            transmitter_uuid = observation_data['transmitter_uuid']
            transmitter = self.transmitters[transmitter_uuid]

            observation = create_new_observation(
                station=observation_data['ground_station'],
                transmitter=transmitter,
                start=observation_data['start'],
                end=observation_data['end'],
                author=self.context['request'].user
            )
            new_observations.append(observation)

        for observation in new_observations:
            observation.save()

        return new_observations

    def update(self, instance, validated_data):
        """Updates observations from a list of validated data

        currently disabled and returns None
        """
        return None


class NewObservationSerializer(serializers.Serializer):
    """SatNOGS Network New Observation API Serializer"""
    start = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'],
        error_messages={
            'invalid':
            'Start datetime should have either \'%Y-%m-%d %H:%M:%S.%f\' or \'%Y-%m-%d %H:%M:%S\' '
            'format.',
            'required':
            'Start(\'start\' key) datetime is required.'
        }
    )
    end = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'],
        error_messages={
            'invalid':
            'End datetime should have either \'%Y-%m-%d %H:%M:%S.%f\' or \'%Y-%m-%d %H:%M:%S\' '
            'format.',
            'required':
            'End datetime(\'end\' key) is required.'
        }
    )
    ground_station = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.filter(status__gt=0),
        allow_null=False,
        error_messages={
            'does_not_exist': 'Station should exist and be online.',
            'required': 'Station(\'ground_station\' key) is required.'
        }
    )
    transmitter_uuid = serializers.CharField(
        max_length=22,
        min_length=22,
        error_messages={
            'invalid': 'Transmitter UUID should be valid.',
            'required': 'Transmitter UUID(\'transmitter_uuid\' key) is required.'
        }
    )

    def validate_start(self, value):
        """Validates start datetime of a new observation"""
        try:
            check_start_datetime(value)
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        return value

    def validate_end(self, value):
        """Validates end datetime of a new observation"""
        try:
            check_end_datetime(value)
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        return value

    def validate(self, attrs):
        """Validates combination of start and end datetimes of a new observation"""
        start = attrs['start']
        end = attrs['end']
        try:
            check_start_end_datetimes(start, end)
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        return attrs

    def create(self, validated_data):
        """Creates a new observation

        Currently not implemented and raises exception. If in the future we want to implement this
        serializer accepting and creating observation from single object instead from a list of
        objects, we should remove raising the exception below and implement the validations that
        exist now only on NewObservationListSerializer
        """
        raise serializers.ValidationError(
            "Serializer is implemented for accepting and schedule\
                                           only lists of observations"
        )

    def update(self, instance, validated_data):
        """Updates an observation from validated data

        currently disabled and returns None
        """
        return None

    class Meta:
        list_serializer_class = NewObservationListSerializer


class AntennaSerializer(serializers.ModelSerializer):
    """SatNOGS Network Antenna API Serializer"""
    class Meta:
        model = Antenna
        fields = ('frequency', 'frequency_max', 'band', 'antenna_type')


class StationSerializer(serializers.ModelSerializer):
    """SatNOGS Network Station API Serializer"""
    antenna = AntennaSerializer(many=True)
    altitude = serializers.SerializerMethodField()
    min_horizon = serializers.SerializerMethodField()
    observations = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = (
            'id', 'name', 'altitude', 'min_horizon', 'lat', 'lng', 'qthlocator', 'location',
            'antenna', 'created', 'last_seen', 'status', 'observations', 'description',
            'client_version', 'target_utilization'
        )

    def get_altitude(self, obj):
        """Returns Station elevation"""
        return obj.alt

    def get_min_horizon(self, obj):
        """Returns Station minimum horizon"""
        return obj.horizon

    def get_antenna(self, obj):
        """Returns Station antenna list"""
        def antenna_name(antenna):
            """Returns Station antenna"""
            return antenna.band + " " + antenna.get_antenna_type_display()

        try:
            return [antenna_name(ant) for ant in obj.antenna.all()]
        except AttributeError:
            return None

    def get_observations(self, obj):
        """Returns Station observations number"""
        try:
            return obj.observations_count
        except AttributeError:
            return None

    def get_status(self, obj):
        """Returns Station status"""
        try:
            return obj.get_status_display()
        except AttributeError:
            return None


class JobSerializer(serializers.ModelSerializer):
    """SatNOGS Network Job API Serializer"""
    frequency = serializers.SerializerMethodField()
    tle0 = serializers.SerializerMethodField()
    tle1 = serializers.SerializerMethodField()
    tle2 = serializers.SerializerMethodField()
    mode = serializers.SerializerMethodField()
    transmitter = serializers.SerializerMethodField()
    baud = serializers.SerializerMethodField()

    class Meta:
        model = Observation
        fields = (
            'id', 'start', 'end', 'ground_station', 'tle0', 'tle1', 'tle2', 'frequency', 'mode',
            'transmitter', 'baud'
        )

    def get_frequency(self, obj):
        """Returns Transmitter downlink low frequency"""
        frequency = obj.transmitter_downlink_low
        frequency_drift = obj.transmitter_downlink_drift
        if frequency_drift is None:
            return frequency
        return int(round(frequency + ((frequency * frequency_drift) / 1e9)))

    def get_transmitter(self, obj):
        """Returns Transmitter UUID"""
        return obj.transmitter_uuid

    def get_tle0(self, obj):
        """Returns line 0 of TLE"""
        return obj.tle.tle0

    def get_tle1(self, obj):
        """Returns line 1 of TLE"""
        return obj.tle.tle1

    def get_tle2(self, obj):
        """Returns line 2 of TLE"""
        return obj.tle.tle2

    def get_mode(self, obj):
        """Returns Transmitter mode"""
        try:
            return obj.transmitter_mode
        except AttributeError:
            return ''

    def get_baud(self, obj):
        """Returns Transmitter baudrate"""
        return obj.transmitter_baud


class TransmitterSerializer(serializers.ModelSerializer):
    """SatNOGS Network Transmitter API Serializer"""
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Transmitter
        fields = ('uuid', 'sync_to_db', 'stats')

    def get_stats(self, obj):
        """Returns Transmitter statistics"""
        stats = transmitter_stats_by_uuid(obj.uuid)
        for statistic in stats:
            stats[statistic] = int(stats[statistic])
        return stats
