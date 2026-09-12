import os
import platform
import resource
import struct

from pydantic import BaseModel

from cezzis_com_cloudsync_api.application.concerns.health.app_version import get_app_version


class PingRs(BaseModel):
    machine_name: str
    version: str
    is_64bit_os: bool
    is_64bit_process: bool
    processor_count: int
    os_version: str
    working_set: int

    @staticmethod
    def create() -> "PingRs":
        return PingRs(
            machine_name=platform.node(),
            version=get_app_version(),
            is_64bit_os=struct.calcsize("P") * 8 == 64,
            is_64bit_process=struct.calcsize("P") * 8 == 64,
            processor_count=os.cpu_count() or 0,
            os_version=platform.platform(),
            working_set=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        )
