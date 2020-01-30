"""
    Health Services
    ______________
    module to check health for db, external service, etc...
"""
import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from celery import group

from app.api import db, sentry

# task
from task.transaction.tasks import TransactionTask
from task.bank.tasks import BankTask
from task.payment.tasks import PaymentTask
from task.utility.tasks import UtilityTask


def str_to_class(class_name):
    return getattr(sys.modules[__name__], class_name)


class HealthServices:
    @staticmethod
    def _check_db():
        """ method to check db that we connect """
        try:
            # execute raw query
            sql = text("SELECT * from bank")
            result = db.engine.execute(sql)
        except SQLAlchemyError as e:
            if not current_app.testing and not current_app.debug:
                sentry.captureException(e)
            # end if
            return False
        # end try
        return True

    # end def

    @staticmethod
    def _convert_state_to_bool(task):
        """ convert known celery task state into boolean """
        worker_status = True
        if task.completed_count() != 4:  # no of known worker
            worker_status = False
        return worker_status

    # end def

    @staticmethod
    def _convert_http_to_bool(status_code):
        """ convert known http status code from external service into boolean """
        result = True
        if status_code != 200:
            result = False
        return result

    # end def

    @staticmethod
    def _calculate_length(_dict):
        length = 0
        for key, value in _dict.items():
            if isinstance(value, dict):
                for key, value in value.items():
                    length += 1
                # end for
            else:
                length += 1
            # end if
        # end for
        return length

    def _convert_to_percentage(self, _dict):
        # first check how many item inside dict
        length = self._calculate_length(_dict)
        score = 0
        for key, value in _dict.items():
            if isinstance(value, dict):
                for key, value in value.items():
                    if value:
                        score += 1
                    # end if
                # end for
            elif value:
                score += 1
            # end if
        # end for
        return round(score / length * 100, 1)

    def _check_worker(self):
        """ method to check all worker that we connect """
        # iterate to all known worker
        workers = [
            {"name": "TransactionTask", "queue": "transaction"},
            {"name": "BankTask", "queue": "bank"},
            {"name": "PaymentTask", "queue": "payment"},
            {"name": "UtilityTask", "queue": "utility"},
        ]

        job_group = group(
            [
                str_to_class(wrk["name"])()
                .health_check.s("CHECK")
                .set(queue=wrk["queue"])
                for wrk in workers
            ]
        )

        result = job_group.apply_async()
        return self._convert_state_to_bool(result)

    def check(self):
        """ inteface method to check various health modules """
        health_status = {}
        # check db connection
        health_status["db"] = self._check_db()
        # check worker connection
        health_status["worker"] = self._check_worker()
        # calcaulate overall percentage of current health
        health_status["hp"] = self._convert_to_percentage(health_status)
        return health_status
