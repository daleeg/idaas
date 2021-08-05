import time
import logging
import os
import time

LOG = logging.getLogger(__name__)

try:
    TWEPOCH = int(os.getenv("SNOW_GENESIS", 1605064271000))
except:
    # 2020-11-11 11:11:11.000
    TWEPOCH = 1605064271000


class InputError(Exception):
    pass


class InvalidSystemClock(Exception):
    pass


class InvalidUserAgentError(Exception):
    pass


class SnowIdWorker(object):
    def __init__(self, worker_id=0, dc=0):
        self.worker_id = worker_id
        self.dc = dc
        # stats
        self.ids_generated = 0
        self.twepoch = TWEPOCH
        self.sequence = 0
        self.worker_id_bits = 6
        self.dc_bits = 4
        self.sequence_bits = 11
        self.reserve_bits = 1

        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_dc = -1 ^ (-1 << self.dc_bits)

        self.worker_id_lshift = self.sequence_bits
        self.dc_lshift = self.sequence_bits + self.worker_id_bits
        self.timestamp_lshift = self.sequence_bits + self.worker_id_bits + self.dc_bits
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)
        self._last = int(time.time() * 1000) - 1
        self.cache = ((self._last - self.twepoch) << self.timestamp_lshift) | (
                self.dc << self.dc_lshift) | (
                             self.worker_id << self.worker_id_lshift)
        self.tail = 0

        # Sanity check for worker_id
        if self.worker_id > self.max_worker_id or self.worker_id < 0:
            raise InputError("worker_id", f"worker id can't be greater than {self.max_worker_id} or less than 0")

        if self.dc > self.max_dc or self.dc < 0:
            raise InputError("dc",
                             f"data center id can't be greater than {self.max_dc} or less than 0")

        LOG.info(f"worker starting. current left shift {self.timestamp_lshift}, "
                 f"data center id bits {self.dc_bits}, worker id bits{self.worker_id_bits}, "
                 f"sequence bits {self.sequence_bits}, worker id {self.worker_id}")

    def _next_id(self):
        current = self.get_current()
        self.sequence = (self.sequence + 1) & self.sequence_mask
        if self.sequence == 0:
            current = self.get_next_tick()
            self.sequence = 1
        if self.sequence == 1:
            self.cache = ((current - self.twepoch) << self.timestamp_lshift) | (
                    self.dc << self.dc_lshift) | (
                                 self.worker_id << self.worker_id_lshift)

        self._last = current
        new_id = self.cache | self.sequence << self.reserve_bits | self.tail
        self.tail = self.tail ^ 1
        self.ids_generated += 1
        return new_id

    def get_current(self):
        if 0 < self.sequence < self.sequence_mask:
            return self._last
        return self.get_next_tick()

    def get_next_tick(self):
        current = int(time.time() * 1000)
        if self._last > current:
            LOG.warning(f"clock is moving backwards. Rejecting request until {self._last}")
            raise InvalidSystemClock(
                f"Clock moved backwards. Refusing to generate id for {self._last} milliseconds")
        if self._last == current:
            time.sleep(0.0001)
            print("sleep")
            current = int(time.time() * 1000)
        return current

    def get_id(self):
        new_id = self._next_id()
        LOG.debug(f"id: {new_id} worker_id: {self.worker_id}  dc: {self.dc}")
        return new_id


class SnowIdWorkerPool(object):
    cache = {}

    @classmethod
    def get_id(cls, worker_id=0, dc=0):
        key = f"{dc}-{worker_id}"
        _flake = cls.cache.setdefault(key, SnowIdWorker(worker_id, dc))
        return _flake.get_id()


snow_flake = SnowIdWorkerPool()
