"""Module for calculating and keep in cache satellite and transmitter statistics"""
from __future__ import absolute_import, division

import math

from django.core.cache import cache
from django.db.models import Case, IntegerField, Sum, When
from django.utils.timezone import now

from network.base.models import Observation


def transmitter_stats_by_uuid(uuid):
    """Calculate and put in cache transmitter statistics"""
    stats = cache.get('tr-{0}-stats'.format(uuid))
    if stats is None:
        # Sum - Case - When should be replaced with Count and filter when we move to Django 2.*
        # more at https://docs.djangoproject.com/en/2.2/ref/models/conditional-expressions in
        # "Conditional aggregation" section.
        stats = Observation.objects.filter(transmitter_uuid=uuid).exclude(
            vetted_status='failed'
        ).aggregate(
            good=Sum(Case(When(vetted_status='good', then=1), output_field=IntegerField())),
            bad=Sum(Case(When(vetted_status='bad', then=1), output_field=IntegerField())),
            unvetted=Sum(
                Case(
                    When(vetted_status='unknown', end__lte=now(), then=1),
                    output_field=IntegerField()
                )
            ),
            future=Sum(
                Case(
                    When(vetted_status='unknown', end__gt=now(), then=1),
                    output_field=IntegerField()
                )
            )
        )
        cache.set('tr-{0}-stats'.format(uuid), stats, 3600)

    total_count = 0
    unvetted_count = 0 if stats['unvetted'] is None else stats['unvetted']
    future_count = 0 if stats['future'] is None else stats['future']
    good_count = 0 if stats['good'] is None else stats['good']
    bad_count = 0 if stats['bad'] is None else stats['bad']
    total_count = unvetted_count + future_count + good_count + bad_count
    unvetted_rate = 0
    future_rate = 0
    success_rate = 0
    bad_rate = 0

    if total_count:
        unvetted_rate = math.trunc(10000 * (float(unvetted_count) / float(total_count))) / 100.0
        future_rate = math.trunc(10000 * (float(future_count) / float(total_count))) / 100.0
        success_rate = math.trunc(10000 * (float(good_count) / float(total_count))) / 100.0
        bad_rate = math.trunc(10000 * (float(bad_count) / float(total_count))) / 100.0

    return {
        'total_count': total_count,
        'unvetted_count': unvetted_count,
        'future_count': future_count,
        'good_count': good_count,
        'bad_count': bad_count,
        'unvetted_rate': unvetted_rate,
        'future_rate': future_rate,
        'success_rate': success_rate,
        'bad_rate': bad_rate
    }


def satellite_stats_by_transmitter_list(transmitter_list):
    """Calculate satellite statistics"""
    total_count = 0
    unvetted_count = 0
    future_count = 0
    good_count = 0
    bad_count = 0
    unvetted_rate = 0
    future_rate = 0
    success_rate = 0
    bad_rate = 0
    for transmitter in transmitter_list:
        transmitter_stats = transmitter_stats_by_uuid(transmitter['uuid'])
        total_count += transmitter_stats['total_count']
        unvetted_count += transmitter_stats['unvetted_count']
        future_count += transmitter_stats['future_count']
        good_count += transmitter_stats['good_count']
        bad_count += transmitter_stats['bad_count']

    if total_count:
        unvetted_rate = math.trunc(10000 * (float(unvetted_count) / float(total_count))) / 100.0
        future_rate = math.trunc(10000 * (float(future_count) / float(total_count))) / 100.0
        success_rate = math.trunc(10000 * (float(good_count) / float(total_count))) / 100.0
        bad_rate = math.trunc(10000 * (float(bad_count) / float(total_count))) / 100.0

    return {
        'total_count': total_count,
        'unvetted_count': unvetted_count,
        'future_count': future_count,
        'good_count': good_count,
        'bad_count': bad_count,
        'unvetted_rate': unvetted_rate,
        'future_rate': future_rate,
        'success_rate': success_rate,
        'bad_rate': bad_rate
    }
