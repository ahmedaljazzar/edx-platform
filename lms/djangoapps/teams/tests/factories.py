"""Factories for testing the Teams API."""

from contextlib import contextmanager

import pytz
from datetime import datetime
from uuid import uuid4

from mock import patch
from django.test.client import RequestFactory
import factory
from factory.django import DjangoModelFactory

from request_cache import get_request
from ..search_indexes import CourseTeamIndexer
from ..models import CourseTeam, CourseTeamMembership


LAST_ACTIVITY_AT = datetime(2015, 8, 15, 0, 0, 0, tzinfo=pytz.utc)


class CourseTeamFactory(DjangoModelFactory):
    """Factory for CourseTeams.

    Note that team_id is not auto-generated from name when using the factory.
    """
    FACTORY_FOR = CourseTeam
    FACTORY_DJANGO_GET_OR_CREATE = ('team_id',)

    team_id = factory.Sequence('team-{0}'.format)
    discussion_topic_id = factory.LazyAttribute(lambda a: uuid4().hex)
    name = "Awesome Team"
    description = "A simple description"
    last_activity_at = LAST_ACTIVITY_AT


class CourseTeamMembershipFactory(DjangoModelFactory):
    """Factory for CourseTeamMemberships."""
    FACTORY_FOR = CourseTeamMembership
    last_activity_at = LAST_ACTIVITY_AT

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create the team membership. """
        with stub_team_index_request():
            obj = model_class(*args, **kwargs)
            obj.save()
            return obj


@contextmanager
def stub_team_index_request():
    # Django Rest Framework v3 requires us to pass a request to serializers
    # that have URL fields.  Since we're invoking this code outside the context
    # of a request, we need to simulate that there's a request.
    if get_request() is None:
        with patch.object(CourseTeamIndexer, "_get_request") as mock_get_request:
            mock_get_request.returns = RequestFactory().get("/")
            yield

    else:
        yield
