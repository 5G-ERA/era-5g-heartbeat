import logging
import os
import sys
from typing import Dict, Tuple
from urllib.parse import urlparse

import psutil
from pythonping import executor, ping

from era_5g_interface.channels import DATA_ERROR_EVENT, DATA_NAMESPACE, CallbackInfoServer, ChannelType
from era_5g_interface.dataclasses.control_command import ControlCmdType, ControlCommand
from era_5g_interface.interface_helpers import HEARTBEAT_CLIENT_EVENT, MIDDLEWARE_ADDRESS, HeartbeatSender
from era_5g_server.server import NetworkApplicationServer

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Heartbeat module")

# Port of the Heartbeat Module server.
HEARTBEAT_PORT = int(os.getenv("HEARTBEAT_PORT", 5898))

# Middleware robot ID (robot ID).
MIDDLEWARE_ROBOT_ID = str(os.getenv("MIDDLEWARE_ROBOT_ID", "00000000-0000-0000-0000-000000000000"))

ROBOT_STATUS_ADDRESS = (
    MIDDLEWARE_ADDRESS if MIDDLEWARE_ADDRESS.endswith("/status/robot") else MIDDLEWARE_ADDRESS + "/status/robot"
)


def generate_heartbeat_data() -> Dict:
    """Generate robot heartbeat JSON data."""

    battery_status = psutil.sensors_battery()

    data = {
        "id": MIDDLEWARE_ROBOT_ID,  # String
        "actionSequenceId": None,  # Optional, integer
        "currentlyExecutedActionIndex": None,  # Optional, integer
        "batteryLevel": int(battery_status.percent if battery_status else 100),  # Robot battery level, integer
        "cpuUtilisation": psutil.cpu_percent(percpu=False),  # Robot CPU utilization, float
        "ramUtilisation": psutil.virtual_memory().percent,  # Robot RAM utilization, float
    }
    return data


class HeartbeatModule(NetworkApplicationServer):
    """Heartbeat Module server communicates with 5G-ERA Network Application clients, with Central API, and manages
    periodic status information about robot (CPU, RAM, etc.) and sends it to 5G-ERA Middleware."""

    def __init__(
        self,
        **kwargs,
    ) -> None:
        """Constructor.

        Args:
            *args: NetworkApplicationServer arguments.
            **kwargs: NetworkApplicationServer arguments.
        """

        super().__init__(
            callbacks_info={
                HEARTBEAT_CLIENT_EVENT: CallbackInfoServer(ChannelType.JSON, self.info_callback),
            },
            **kwargs,
        )
        self.tasks: Dict[str, str] = dict()

        self.heartbeat_sender = HeartbeatSender(ROBOT_STATUS_ADDRESS, generate_heartbeat_data)

    def info_callback(self, sid: str, data: Dict) -> Dict:
        """Allows to receive general info json data using the websocket transport.

        Args:
            sid (str): Namespace sid.
            data (Dict): 5G-ERA Network Application specific JSON data.
        """

        eio_sid = self._sio.manager.eio_sid_from_sid(sid, DATA_NAMESPACE)

        if eio_sid not in self.tasks:
            logger.error(f"Non-registered client {eio_sid} tried to send data")
            self.send_data({"message": "Non-registered client tried to send data"}, DATA_ERROR_EVENT, sid=sid)
            return {}

        logger.info(f"Client with id: {self.get_eio_sid_of_data(sid)} sent data {data}")

        # Example, how to test the latency of middleware address.
        response_list: executor.ResponseList = ping(urlparse("//" + MIDDLEWARE_ADDRESS).hostname, verbose=True)
        logger.info(f"Average {MIDDLEWARE_ADDRESS} rtt {response_list.rtt_avg_ms}ms")

        return {MIDDLEWARE_ADDRESS: response_list.rtt_avg_ms}

    def command_callback(self, command: ControlCommand, sid: str) -> Tuple[bool, str]:
        """Process initialization control command - creates client info.

        Args:
            command (ControlCommand): Control command to be processed.
            sid (str): Namespace sid.

        Returns:
            (initialized (bool), message (str)): If False, initialization failed.
        """

        eio_sid = self.get_eio_sid_of_control(sid)

        logger.info(f"Control command {command} processing: session id: {sid}")

        if command and command.cmd_type == ControlCmdType.INIT:
            # Check that initialization has not been called before.
            if eio_sid in self.tasks:
                logger.error("Client attempted to call initialization multiple times")
                self.send_command_error("Initialization has already been called before", sid)
                return False, "Initialization has already been called before"

            self.tasks[eio_sid] = sid

        logger.info(
            f"Control command applied, eio_sid {eio_sid}, sid {sid}, "
            f"results sid {self.get_sid_of_data(eio_sid)}, command {command}"
        )
        return True, (
            f"Control command applied, eio_sid {eio_sid}, sid {sid}, results sid"
            f" {self.get_sid_of_data(eio_sid)}, command {command}"
        )

    def disconnect_callback(self, sid: str) -> None:
        """Called with client disconnection - deletes client info.

        Args:
            sid (str): Namespace sid.
        """

        eio_sid = self.get_eio_sid_of_data(sid)
        del self.tasks[eio_sid]

        logger.info(f"Client disconnected from {DATA_NAMESPACE} namespace, eio_sid {eio_sid}, sid {sid}")


def main() -> None:
    """Main function."""

    heartbeat_module = HeartbeatModule(port=HEARTBEAT_PORT, host="0.0.0.0")

    try:
        heartbeat_module.run_server()
    except KeyboardInterrupt:
        logger.info("Terminating ...")


if __name__ == "__main__":
    main()
