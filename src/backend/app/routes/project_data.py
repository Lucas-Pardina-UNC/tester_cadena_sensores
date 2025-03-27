import json
import uuid
from typing import Union
from pymodbus.client import AsyncModbusSerialClient
from framer_selector import get_framer #from pymodbus import FramerType

Framer = get_framer()
class Slave:
    def __init__(self, slave_id : int, sensor_id: Union[str, int], sensor_type: str):
        self.slave_id = slave_id
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type

    def to_dict(self):
        return {
            "slave_id": self.slave_id,
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type
        }
class Chain:
    def __init__(self, chain_port, baudrate, bytesize, parity, stopbits, timeout, chain_protocol, chain_available_slaves, chain_id, result_columns):
        self.chain_port = chain_port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.chain_protocol = chain_protocol
        self.chain_available_slaves = chain_available_slaves
        self.id = chain_id
        self.result_columns = result_columns
        self.chain_client = None  # Placeholder for the client object

        # Convert dictionaries back into Slave objects
        self.chain_available_slaves = [
            Slave(**slave) if isinstance(slave, dict) else slave
            for slave in chain_available_slaves
        ]

        if self.chain_protocol == "modbus":
            self.chain_client = AsyncModbusSerialClient(
                port=self.chain_port,
                framer=Framer,  # Use Framer (framer_selector.py) instead of FramerType.RTU for retrocompatiiility
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
            )

    def to_dict(self):
        """
        Export chain details to a dictionary (excluding the client object).
        """
        return {
            "chain_port": self.chain_port,
            "baudrate": self.baudrate,
            "bytesize": self.bytesize,
            "parity": self.parity,
            "stopbits": self.stopbits,
            "timeout": self.timeout,
            "chain_protocol": self.chain_protocol,
            "chain_available_slaves": self.chain_available_slaves,
            "id": self.id,
            "result_columns": self.result_columns,
        }


class Project:
    def __init__(self):
        self.id = str(uuid.uuid4())  # Automatically generate a unique project ID
        self.name = ""
        self.project_folder = ""
        self.num_chains = 0
        self.chains = []  # This will hold a list of Chain objects

    def add_chain(self, chain_data):
        """
        Create a Chain object from the provided data and add it to the chains list.
        """
        chain = Chain(
            chain_port=chain_data["chain_port"],
            baudrate=chain_data["baudrate"],
            bytesize=chain_data["bytesize"],
            parity=chain_data["parity"],
            stopbits=chain_data["stopbits"],
            timeout=chain_data["timeout"],
            chain_protocol=chain_data["chain_protocol"],
            chain_available_slaves=chain_data["chain_available_slaves"],
            chain_id=chain_data["id"],
            result_columns=chain_data["result_columns"],
        )
        self.chains.append(chain)
        #self.num_chains += 1

    def from_json(self, file_path):
        """
        Load project details and chains from a JSON file.
        """
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        self.id = data.get("id", str(uuid.uuid4()))
        self.name = data["name"]
        self.project_folder = data["project_folder"]
        self.num_chains = data["num_chains"]
        self.chains = []

        for chain_data in data["chains"]:
            self.add_chain(chain_data) 

    def to_json(self):
        """
        Export the current project as a JSON string.
        """
        export_data = {
            "id": self.id,
            "name": self.name,
            "project_folder": self.project_folder,
            "num_chains": self.num_chains,
            "chains": [chain.to_dict() for chain in self.chains],
        }
        return json.dumps(export_data, indent=4)


# Singleton instance of the Project class
project_instance = Project()


def load_project_from_file(file_path):
    """
    Load the project instance with data from a JSON file.
    """
    project_instance.from_json(file_path)


def get_project_instance():
    """
    Access the singleton project instance.
    """
    return project_instance
