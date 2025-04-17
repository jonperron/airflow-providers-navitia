# mypy: ignore-errors
# pylint: disable-all

"""
Unittest module to test Hook

Requires the unittest, pytest and requests-mock Python libraries

Run test:
    python3 -m unittest tests.hooks.test_navitia_hook.TestNavitiaHook
"""

import logging
import pytest
from unittest.mock import Mock, patch

from airflow.models import Connection
from airflow.utils import db
from navitia_client.client import NavitiaClient
from navitia_client.client.exceptions import NavitiaForbiddenAccessError

from navitia_provider.hooks.navitia import NavitiaHook

log = logging.getLogger(__name__)

pytestmark = pytest.mark.db_test

navitia_client_mock = Mock(name="navitia_client_for_test")


class TestNavitiaHook:
    def setup_class(self) -> None:
        db.merge_conn(
            Connection(
                conn_id="navitia_default",
                conn_type="navitia",
                password="my-super-token",
            )
        )

    @patch(
        "navitia_provider.hooks.navitia.LokaliseClient",
        autospec=True,
        return_value=navitia_client_mock,
    )
    def test_navitia_client_connection(self, navitia_mock) -> None:
        navitia_hook = NavitiaHook()

        assert navitia_mock.called
        assert isinstance(navitia_hook.client, Mock)
        assert navitia_hook.client.name == navitia_mock.return_value.name

    def test_connection_success(self) -> None:
        hook = NavitiaHook()
        hook.client = Mock(spec=NavitiaClient)

        status, msg = hook.test_connection()

        assert status is True
        assert msg == "Successfully connected to Navitia."

    def test_connection_failure(self) -> None:
        hook = NavitiaClient()
        hook.client.project = Mock(
            side_effect=NavitiaForbiddenAccessError
        )

        status, msg = hook.test_connection()

        assert status is False
        assert msg == "('API token is incorrect', 401)"
