import time
from ctypes import WinDLL
from pathlib import Path

from util.logging import logger


class ParallelPortTrigger:
    def __init__(self, enabled=False, address=0x378, dll_path=None, pulse_width_ms=5, reset_to_zero=True):
        self.enabled = enabled
        self.address = int(address)
        self.dll_path = dll_path
        self.pulse_width_ms = float(pulse_width_ms)
        self.reset_to_zero = bool(reset_to_zero)
        self._out32 = None

        if not self.enabled:
            logger.warning('[PARALLEL_PORT][SKIP] trigger disabled by configuration')
            return

        if not self.dll_path:
            logger.error('[PARALLEL_PORT][FAIL] enabled, but no dll_path was configured')
            self.enabled = False
            return

        dll_file = Path(self.dll_path)
        if not dll_file.exists():
            logger.error(f'[PARALLEL_PORT][FAIL] DLL not found: {dll_file}')
            self.enabled = False
            return

        try:
            dll = WinDLL(str(dll_file))
            self._out32 = dll.Out32
            logger.success(
                f'[PARALLEL_PORT][READY] address=0x{self.address:03X}, '
                f'dll={dll_file}, pulse_width_ms={self.pulse_width_ms:g}, reset_to_zero={self.reset_to_zero}'
            )
        except Exception as err:
            logger.exception(f'[PARALLEL_PORT][FAIL] initialization failed: {err}')
            self.enabled = False

    def send(self, code):
        code = int(code)

        if not self.enabled or self._out32 is None:
            logger.warning(
                f'[PARALLEL_PORT][SKIP] code=0x{code:02X}, address=0x{self.address:03X}, '
                'trigger not available'
            )
            return

        try:
            self._out32(self.address, code)
            if self.reset_to_zero:
                time.sleep(self.pulse_width_ms / 1000.0)
                self._out32(self.address, 0)
            logger.success(
                f'[PARALLEL_PORT][OK] code=0x{code:02X}, address=0x{self.address:03X}, '
                f'pulse_width_ms={self.pulse_width_ms:g}, reset_to_zero={self.reset_to_zero}'
            )
        except Exception as err:
            logger.exception(
                f'[PARALLEL_PORT][FAIL] code=0x{code:02X}, address=0x{self.address:03X}, error={err}'
            )
