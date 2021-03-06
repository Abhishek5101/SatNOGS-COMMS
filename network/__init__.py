"""The core django app for SatNOGS Network"""
from __future__ import absolute_import

from ._version import get_versions
from .celery import APP as celery_app  # noqa

__all__ = ['celery_app']

__version__ = get_versions()['version']
del get_versions
