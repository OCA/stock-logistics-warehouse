# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from time import sleep
from typing import Union
from urllib.parse import urljoin

import requests

_logger = logging.getLogger(__name__)

MODULA_KEYS = [
    "task_type",
    "task_id",
    "address",
    "carrier",
    "pos_x",
    "pos_y",
    "qty",
    "info1",
    "info2",
    "info3",
    "info4",
]


MODULA_OPERATION_CODES = {
    "release": False,  # TODO: Find out operation to release trays
    "put": "V",
    "get": "P",
    "count": False,
}


class ModulaRequest:
    """
    Interface to Modula Driver Webservices

    The command workflow goes as this:
    1.- We send the task (or tasks) to the Modula Driver agent. We'll just get an 200
        response. (/api/jobs/CFG-IMP-ESEGUI)
    2.- The Modula Driver agent sends it to the VLM and hopefully the operator do the
        requested tasks.
    3.- In order to know if a task is completed, we have to request it to the Modula
        Driver agent (/api/jobs/CFG-EXP-ESEGUI). This is a simple get request that
        gives us all the current tasks info.
    4.- So we have to be querying the agent until the task is completed.
    5.- We only get to know that:
        - The task was completed.
        - The quantity that was done by the operator.
    6.- Once it's completed and we complete the Odoo task side, we have to send an
        ACK to the agent with the unique task id (GUID) that we gathered before. The
        task will be deleted from the agent at this moment.
    """

    def __init__(self, ip, port, timeout=5, user=None, password=None, **kw):
        self.ip = ip
        self.port = int(port)
        #
        self.timeout = timeout or None
        self.user = user
        self.password = password
        self.url = f"http://{self.ip}:{self.port}"

    def _prepare_request(self, data: Union[dict, list]) -> dict:
        """Standard Modula WMS request. They keys could be customized but it's not
        supported at this moment. The method can be overriden tho."""
        if isinstance(data, dict):
            data = [data]
        orders = [
            {
                "ORD_ORDINE": task["task_id"],
                "ORD_DES": task["info1"],
                "ORD_TIPOOP": MODULA_OPERATION_CODES[task["task_type"]],
            }
            for task in data
        ]
        requests = [
            {
                "RIG_ORDINE": task["task_id"],
                "RIG_ARTICOLO": task["info2"][:50],
                "RIG_HOSTINF": i + 1,
                "RIG_UDC": task["carrier"],
                "RIG_QTAR": task["qty"].replace(".", ","),
                "RIG_UMI": "Uds",
                "RIG_POSX": task["pos_x"],
                "RIG_POSY": task["pos_y"],
            }
            for i, task in enumerate(data)
        ]
        return {
            "IMP_ESEGUI_ORDINI": orders,
            "IMP_ESEGUI_ORDINI_RIGHE": requests,
        }

    def _task_state(self, data: dict, task: str) -> tuple:
        """Parse Modula export response to get statuses"""
        job_id = data.get("GUID")
        orders = data.get("DATA", {}).get("EXP_ESEGUI_ORDINI", [])
        task_in_orders = any([task == o.get("ORD_ORDINE") for o in orders])
        state = data.get("TransactionStatus", "pending")
        if state == "END" and task_in_orders:
            state = "done"
        return (job_id, state)

    def _parse_data(self, data: dict) -> dict:
        """Parse data to get task quantities"""
        orders = data.get("DATA", {}).get("EXP_ESEGUI_ORDINI_RIGHE", [])
        return {"qty": orders[0]["RIG_QTAE"].replace(",", ".")}

    def _export_job(self, data: dict) -> requests.models.Response:
        """Send jobs to command the VLM"""
        return requests.post(
            urljoin(self.url, "/api/jobs/CFG-IMP-ESEGUI"),
            auth=(self.user, self.password),
            json=data,
            timeout=self.timeout,
            headers={"User-Agent": "Custom", "Accept": "application/json"},
        )

    def _gather_jobs(self, timeout: float = 5) -> requests.models.Response:
        """Retrieve jobs ids and states"""
        return requests.get(
            urljoin(self.url, "/api/jobs/CFG-EXP-ESEGUI"),
            auth=(self.user, self.password),
            timeout=timeout,
        )

    def _ack_job(self, job_id: str, timeout: float = 5) -> requests.models.Response:
        """Sent when the tasks are performed in Odoo"""
        return requests.post(
            urljoin(self.url, "/api/jobs/CFG-EXP-ESEGUI/ACK"),
            auth=(self.user, self.password),
            json={"GUID": job_id},
            headers={"User-Agent": "Custom", "Accept": "application/json"},
            timeout=timeout,
        )

    def request_operation(self, data: dict) -> dict:
        _logger.info(f"Request: {data}")
        operation_id = data.get("task_id")
        data = self._prepare_request(data)
        if not operation_id:
            return
        try:
            response = self._export_job(data)
            _logger.info(f"Response: {response} {response.content}")
        except requests.exceptions.ConnectionError:
            return {"code": "-1", "task_id": operation_id}
        except requests.exceptions.ReadTimeout:
            return {"code": "-3", "task_id": operation_id}
        if response.status_code != 200:
            return {"code": "-4", "task_id": operation_id}
        # Response ok, let's wait until the job is finished:
        while True:
            sleep(1)
            response = self._gather_jobs()
            _logger.info(f"Response: {response} {response.content}")
            if response.status_code == 204:
                continue
            if response.status_code != 200:
                return {"code": "-4", "task_id": operation_id}
            data = response.json()
            job, state = self._task_state(data, operation_id)
            _logger.info(f"Data: {data} / job: {job} / state: {state}")
            if state == "done":
                response = self._ack_job(job)
                _logger.info(f"Response: {response}")
                break
        return self._parse_data(data)
