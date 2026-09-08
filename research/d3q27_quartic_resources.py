"""OS counters and preregistered Q012h2 limits, never ndarray-byte proxies.

Windows definitions:
https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex
https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/ns-sysinfoapi-memorystatusex
PeakPagefileUsage is peak private commit, not the resident working set.
"""

import ctypes
import os
import shutil
from pathlib import Path
from time import perf_counter

GIB = 1024**3
PEAK_LIMIT = 3 * GIB
TIME_LIMIT = 4 * 3600
DISK_LIMIT = 2 * GIB


class ProcessMemory(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_uint32), ("PageFaultCount", ctypes.c_uint32)] + [
        (name, ctypes.c_size_t)
        for name in (
            "PeakWorkingSetSize",
            "WorkingSetSize",
            "QuotaPeakPagedPoolUsage",
            "QuotaPagedPoolUsage",
            "QuotaPeakNonPagedPoolUsage",
            "QuotaNonPagedPoolUsage",
            "PagefileUsage",
            "PeakPagefileUsage",
            "PrivateUsage",
        )
    ]


class MemoryStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_uint32), ("dwMemoryLoad", ctypes.c_uint32)] + [
        (name, ctypes.c_uint64)
        for name in (
            "ullTotalPhys",
            "ullAvailPhys",
            "ullTotalPageFile",
            "ullAvailPageFile",
            "ullTotalVirtual",
            "ullAvailVirtual",
            "ullAvailExtendedVirtual",
        )
    ]


def counters():
    if os.name != "nt":
        raise RuntimeError("registered Windows peak-memory counters unavailable on this OS")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.argtypes = []
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.K32GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ProcessMemory),
        ctypes.c_uint32,
    ]
    kernel.K32GetProcessMemoryInfo.restype = ctypes.c_int
    kernel.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MemoryStatus)]
    kernel.GlobalMemoryStatusEx.restype = ctypes.c_int
    current = ProcessMemory()
    current.cb = ctypes.sizeof(current)
    available = MemoryStatus()
    available.dwLength = ctypes.sizeof(available)
    if not kernel.K32GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(current), current.cb
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.GlobalMemoryStatusEx(ctypes.byref(available)):
        raise ctypes.WinError(ctypes.get_last_error())
    return {
        "working_set_bytes": current.WorkingSetSize,
        "peak_working_set_bytes": current.PeakWorkingSetSize,
        "private_commit_bytes": current.PrivateUsage,
        "peak_private_commit_bytes": current.PeakPagefileUsage,
        "available_physical_bytes": available.ullAvailPhys,
        "total_physical_bytes": available.ullTotalPhys,
    }


def limit_checks(snapshot, seconds, disk_bytes):
    return {
        "peak_working_set": snapshot["peak_working_set_bytes"] <= PEAK_LIMIT,
        "peak_private_commit": snapshot["peak_private_commit_bytes"] <= PEAK_LIMIT,
        "wall_time": 0 <= seconds <= TIME_LIMIT,
        "new_disk": 0 <= disk_bytes <= DISK_LIMIT,
    }


class ResourceLimitError(RuntimeError):
    def __init__(self, message, records):
        super().__init__(message)
        self.resource_records = list(records)


class Guard:
    def __init__(self, output):
        self.output = Path(output)
        self.start = perf_counter()
        self.records = []
        initial = self.sample("process_start")
        if initial["available_physical_bytes"] < 4 * GIB or initial["free_disk_bytes"] < 6 * GIB:
            raise ResourceLimitError(
                "registered starting RAM/disk minimum unavailable", self.records
            )

    def sample(self, stage):
        snapshot = counters()
        seconds = perf_counter() - self.start
        paths = sorted(self.output.parent.glob(self.output.stem + "*"))
        disk_bytes = sum(p.stat().st_size for p in paths if p.is_file())
        checks = limit_checks(snapshot, seconds, disk_bytes)
        row = {
            "stage": stage,
            "wall_seconds": seconds,
            **snapshot,
            "free_disk_bytes": shutil.disk_usage(self.output.parent).free,
            "new_file_bytes": disk_bytes,
            "checks": checks,
        }
        self.records.append(row)
        if not all(checks.values()):
            raise ResourceLimitError(
                f"registered resource ceiling exceeded at {stage}: {checks}", self.records
            )
        return row
