# mypy: ignore-errors
# pylint: disable-all

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from airflow.models import Connection
from airflow.models.dag import DAG
from airflow.utils import db, timezone

from navitia_provider.operators.navitia import NavitiaOperator

pytestmark = pytest.mark.db_test

DEFAULT_DATE = timezone.datetime(2023, 12, 1)
navitia_client_mock = Mock(name="navitia_client_for_test")


class TestNavitiaOperator:
    def setup_class(self) -> None:
        args = {"owner": "airflow", "start_date": DEFAULT_DATE}
        dag = DAG("test_dag_id", default_args=args)
        self.dag = dag
        db.merge_conn(
            Connection(
                conn_id="navitia_default",
                conn_type="navitia",
                password="my-super-token",
                host="default_project",
            )
        )

    def test_operator_init_with_optional_args(self) -> None:
        navitia_operator = NavitiaOperator(
            task_id="test_init_navitia_list_keys", navitia_method="raw._generate_filter_query"
        )

        assert navitia_operator.navitia_method_args == {}
        assert navitia_operator.result_processor is None

    @patch(
        "navitia_provider.hooks.navitia.NavitiaClient",
        autospec=True,
        return_value=navitia_client_mock,
    )
    def test_empty_raw_request(self, navitia_mock) -> None:
        navitia_mock.return_value.raw._generate_filter_query.return_value = navitia_client_mock

        navitia_operator = NavitiaOperator(
            task_id="test_navitia_list_keys",
            navitia_method="raw._generate_filter_query",
            navitia_method_args={"key1": "value1", "key2": "value2"},
            result_processor=lambda r: r.__dict__,
            dag=self.dag,
        )

        navitia_operator.run(
            start_date=DEFAULT_DATE, end_date=DEFAULT_DATE, ignore_ti_state=True
        )

        assert navitia_mock.called
        assert navitia_mock.return_value.raw._generate_filter_query.called
