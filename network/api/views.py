"""SatNOGS Network API django rest framework Views"""
from __future__ import absolute_import

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from requests.exceptions import RequestException
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from network.api import filters, pagination, serializers
from network.api.perms import StationOwnerPermission
from network.base.models import LatestTle, Observation, Station, Transmitter
from network.base.utils import sync_demoddata_to_db
from network.base.validators import NegativeElevationError, \
    ObservationOverlapError, SinglePassError


class ObservationView(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, viewsets.GenericViewSet):
    """SatNOGS Network Observation API view class"""
    queryset = Observation.objects.prefetch_related('satellite', 'demoddata', 'ground_station')
    filter_class = filters.ObservationViewFilter
    permission_classes = [StationOwnerPermission]
    pagination_class = pagination.LinkedHeaderPageNumberPagination

    def get_serializer_class(self):
        """Returns the right serializer depending on http method that is used"""
        if self.request.method == 'POST':
            return serializers.NewObservationSerializer
        return serializers.ObservationSerializer

    def create(self, request, *args, **kwargs):
        """Creates observations from a list of observation data"""
        serializer = self.get_serializer(data=request.data, many=True, allow_empty=False)
        try:
            if serializer.is_valid():
                observations = serializer.save()
                serialized_obs = serializers.ObservationSerializer(observations, many=True)
                data = serialized_obs.data
                response = Response(data, status=status.HTTP_200_OK)
            else:
                data = serializer.errors
                response = Response(data, status=status.HTTP_400_BAD_REQUEST)
        except (NegativeElevationError, SinglePassError, ValidationError, ValueError) as error:
            response = Response(str(error), status=status.HTTP_400_BAD_REQUEST)
        except LatestTle.DoesNotExist:
            data = 'Scheduling failed: Satellite without TLE'
            response = Response(data, status=status.HTTP_501_NOT_IMPLEMENTED)
        except ObservationOverlapError as error:
            response = Response(str(error), status=status.HTTP_409_CONFLICT)
        return response

    def update(self, request, *args, **kwargs):
        """Updates observation with audio, waterfall or demoded data"""
        instance = self.get_object()
        if request.data.get('client_version'):
            instance.ground_station.client_version = request.data.get('client_version')
            instance.ground_station.save()
        if request.data.get('demoddata'):
            try:
                file_path = 'data_obs/{0}/{1}'.format(instance.id, request.data.get('demoddata'))
                instance.demoddata.get(payload_demod=file_path)
                return Response(
                    data='This data file has already been uploaded',
                    status=status.HTTP_403_FORBIDDEN
                )
            except ObjectDoesNotExist:
                demoddata = instance.demoddata.create(payload_demod=request.data.get('demoddata'))
                if Transmitter.objects.get(uuid=instance.transmitter_uuid).sync_to_db:
                    try:
                        sync_demoddata_to_db(demoddata.id)
                    except RequestException:
                        # Sync to db failed, let the periodic task handle the sync to db later
                        pass
        if request.data.get('waterfall'):
            if instance.has_waterfall:
                return Response(
                    data='Watefall has already been uploaded', status=status.HTTP_403_FORBIDDEN
                )
        if request.data.get('payload'):
            if instance.has_audio:
                return Response(
                    data='Audio has already been uploaded', status=status.HTTP_403_FORBIDDEN
                )

        # False-positive no-member (E1101) pylint error:
        # Parent class rest_framework.mixins.UpdateModelMixin provides the 'update' method
        super(ObservationView, self).update(request, *args, **kwargs)  # pylint: disable=E1101
        return Response(status=status.HTTP_200_OK)


class StationView(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """SatNOGS Network Station API view class"""
    queryset = Station.objects.prefetch_related('antenna', 'observations')
    serializer_class = serializers.StationSerializer
    filter_class = filters.StationViewFilter
    pagination_class = pagination.LinkedHeaderPageNumberPagination


class TransmitterView(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """SatNOGS Network Transmitter API view class"""
    queryset = Transmitter.objects.all().order_by('uuid')
    serializer_class = serializers.TransmitterSerializer
    filter_class = filters.TransmitterViewFilter
    pagination_class = pagination.LinkedHeaderPageNumberPagination


class JobView(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """SatNOGS Network Job API view class"""
    queryset = Observation.objects.filter(payload='')
    serializer_class = serializers.JobSerializer
    filter_class = filters.ObservationViewFilter
    filter_fields = ('ground_station')

    def get_queryset(self):
        """Returns queryset for Job API view"""
        queryset = self.queryset.filter(start__gte=now()).prefetch_related('tle')
        ground_station_id = self.request.query_params.get('ground_station', None)
        if ground_station_id and self.request.user.is_authenticated():
            ground_station = get_object_or_404(Station, id=ground_station_id)
            if ground_station.owner == self.request.user:
                lat = self.request.query_params.get('lat', None)
                lon = self.request.query_params.get('lon', None)
                alt = self.request.query_params.get('alt', None)
                if not (lat is None or lon is None or alt is None):
                    ground_station.lat = float(lat)
                    ground_station.lng = float(lon)
                    ground_station.alt = int(alt)
                ground_station.last_seen = now()
                ground_station.save()
        return queryset
