#!/usr/bin/env python3
"""
resource_monitor.py

Lightweight resource monitor for SLURM jobs.

This script monitors the resource usage of a target process and its child
processes at a fixed sampling interval. It writes a CSV file containing:

    - Timestamp
    - Target process CPU usage
    - Target process resident memory usage
    - Target process thread count
    - Node-level memory usage
    - GPU IDs visible to the job
    - GPU memory used/free
    - GPU utilization

Typical use case
----------------
This script is intended to be launched from a SLURM batch script after the main
job command has been started in the background. The SLURM script should pass the
PID of the main job process to this monitor.

Example:

    python resource_monitor.py \\
        --pid 12345 \\
        --output /path/to/resource_monitor_123456.csv \\
        --interval 10

The monitor exits automatically when the target PID no longer exists. It can
also be terminated explicitly by the parent SLURM script.

Important notes
---------------
1. Process monitoring is local to the node where this script runs.
   If your SLURM job spans multiple nodes, this monitor only observes processes
   visible from the node where the monitor is launched.

2. GPU monitoring uses `nvidia-smi`.
   If `nvidia-smi` is unavailable, or if the job is running on a CPU-only node,
   GPU fields are written as "N/A".

3. CPU percent is reported as a summed percentage across the target process and
   its child processes. On a multi-core node, values may exceed 100%.

4. Memory for the target process is reported as resident set size, RSS, summed
   across the target process and children.

5. System memory fields are node-level values, not job-cgroup-limited values.
   For exact SLURM accounting after a job completes, compare this CSV with
   `sacct` or site-specific accounting tools.

Dependencies
------------
Required:
    - Python 3
    - psutil

Optional:
    - nvidia-smi, for GPU monitoring

CSV columns
-----------
timestamp:
    ISO-8601 timestamp for the sample.

process_cpu_percent:
    CPU usage for the target process plus child processes.

process_memory_mb:
    Resident memory usage, in MiB, for the target process plus child processes.

process_threads:
    Number of threads in the target process only.

system_memory_used_mb:
    Node-level used memory in MiB.

system_memory_available_mb:
    Node-level available memory in MiB.

system_memory_percent:
    Node-level memory utilization percentage.

gpu_ids:
    Semicolon-separated list of GPU IDs reported by nvidia-smi.

gpu_memory_used_mb:
    Semicolon-separated GPU memory used values in MiB.

gpu_memory_free_mb:
    Semicolon-separated GPU memory free values in MiB.

gpu_utilization_percent:
    Semicolon-separated GPU utilization percentages.

Developer Information
---------------
  __developer__: "Ajay Khanna"
  __place__: "LANL"
  __date__: "May-01-2026"
"""

from __future__ import annotations

import argparse
import csv
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

CSV_COLUMNS = [
    "timestamp",
    "process_cpu_percent",
    "process_memory_mb",
    "process_threads",
    "system_memory_used_mb",
    "system_memory_available_mb",
    "system_memory_percent",
    "gpu_ids",
    "gpu_memory_used_mb",
    "gpu_memory_free_mb",
    "gpu_utilization_percent",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Monitor CPU, memory, and GPU usage for a process tree."
    )
    parser.add_argument(
        "--pid",
        type=int,
        required=True,
        help="PID of the process to monitor.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="CSV file where resource samples will be written.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=10.0,
        help="Sampling interval in seconds. Default: 10.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to an existing CSV instead of overwriting it.",
    )
    return parser.parse_args()


def get_process_stats(pid: int) -> dict[str, float | int] | None:
    """
    Return CPU, memory, and thread statistics for a process tree.

    Parameters
    ----------
    pid:
        Process ID of the root process to monitor.

    Returns
    -------
    dict or None
        Dictionary containing:
            - cpu_percent
            - memory_mb
            - num_threads

        Returns None if the process no longer exists or cannot be accessed.
    """
    try:
        proc = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

    try:
        cpu_percent = proc.cpu_percent(interval=0.1)
        memory_mb = proc.memory_info().rss / (1024 * 1024)
        num_threads = proc.num_threads()

        for child in proc.children(recursive=True):
            try:
                cpu_percent += child.cpu_percent(interval=0.01)
                memory_mb += child.memory_info().rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "num_threads": num_threads,
        }

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def get_system_stats() -> dict[str, float]:
    """
    Return node-level virtual memory statistics.

    Returns
    -------
    dict
        Dictionary containing:
            - memory_used_mb
            - memory_available_mb
            - memory_percent
    """
    vm = psutil.virtual_memory()
    return {
        "memory_used_mb": vm.used / (1024 * 1024),
        "memory_available_mb": vm.available / (1024 * 1024),
        "memory_percent": vm.percent,
    }


def get_gpu_vram_stats() -> list[dict[str, Any]]:
    """
    Return GPU memory and utilization statistics using nvidia-smi.

    Returns
    -------
    list of dict
        One dictionary per GPU, containing:
            - gpu_id
            - gpu_name
            - memory_total_mb
            - memory_used_mb
            - memory_free_mb
            - utilization_percent

        Returns an empty list if nvidia-smi is unavailable or fails.
    """
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    if result.returncode != 0:
        return []

    gpus: list[dict[str, Any]] = []

    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue

        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 6:
            continue

        try:
            gpus.append(
                {
                    "gpu_id": parts[0],
                    "gpu_name": parts[1],
                    "memory_total_mb": float(parts[2]),
                    "memory_used_mb": float(parts[3]),
                    "memory_free_mb": float(parts[4]),
                    "utilization_percent": float(parts[5]),
                }
            )
        except ValueError:
            continue

    return gpus


def format_gpu_fields(gpu_stats: list[dict[str, Any]]) -> tuple[str, str, str, str]:
    """
    Convert GPU statistics into semicolon-separated CSV fields.

    Parameters
    ----------
    gpu_stats:
        List of GPU dictionaries returned by get_gpu_vram_stats().

    Returns
    -------
    tuple
        gpu_ids, gpu_memory_used_mb, gpu_memory_free_mb, gpu_utilization_percent
    """
    if not gpu_stats:
        return "N/A", "N/A", "N/A", "N/A"

    gpu_ids = ";".join(str(gpu["gpu_id"]) for gpu in gpu_stats)
    gpu_mem_used = ";".join(str(int(gpu["memory_used_mb"])) for gpu in gpu_stats)
    gpu_mem_free = ";".join(str(int(gpu["memory_free_mb"])) for gpu in gpu_stats)
    gpu_util = ";".join(str(int(gpu["utilization_percent"])) for gpu in gpu_stats)

    return gpu_ids, gpu_mem_used, gpu_mem_free, gpu_util


def write_header_if_needed(output_file: Path, append: bool) -> None:
    """
    Create the output directory and write the CSV header when needed.

    Parameters
    ----------
    output_file:
        Path to the CSV output file.

    append:
        If True, preserve existing file contents and only write the header when
        the file does not already exist or is empty.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    should_write_header = True

    if append and output_file.exists() and output_file.stat().st_size > 0:
        should_write_header = False

    if should_write_header:
        with output_file.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()


def append_sample(output_file: Path, row: dict[str, Any]) -> None:
    """
    Append one monitoring sample to the CSV file and force it to disk.

    This improves robustness when a SLURM job is cancelled, killed, or reaches
    walltime. It cannot save a sample that was never collected, but it reduces
    the chance of losing buffered CSV data.
    """
    with output_file.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writerow(row)
        handle.flush()
        os.fsync(handle.fileno())


def monitor(pid: int, output_file: Path, interval: float, append: bool = False) -> int:
    """
    Monitor a process tree until the root process exits.

    Parameters
    ----------
    pid:
        Root process ID to monitor.

    output_file:
        Destination CSV file.

    interval:
        Sampling interval in seconds.

    append:
        Whether to append to an existing file.

    Returns
    -------
    int
        Exit code. Zero indicates normal monitor termination.
    """
    write_header_if_needed(output_file, append=append)

    while True:
        proc_stats = get_process_stats(pid)
        if proc_stats is None:
            return 0

        sys_stats = get_system_stats()
        gpu_stats = get_gpu_vram_stats()
        gpu_ids, gpu_mem_used, gpu_mem_free, gpu_util = format_gpu_fields(gpu_stats)

        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "process_cpu_percent": f"{proc_stats['cpu_percent']:.1f}",
            "process_memory_mb": f"{proc_stats['memory_mb']:.1f}",
            "process_threads": proc_stats["num_threads"],
            "system_memory_used_mb": f"{sys_stats['memory_used_mb']:.1f}",
            "system_memory_available_mb": f"{sys_stats['memory_available_mb']:.1f}",
            "system_memory_percent": f"{sys_stats['memory_percent']:.1f}",
            "gpu_ids": gpu_ids,
            "gpu_memory_used_mb": gpu_mem_used,
            "gpu_memory_free_mb": gpu_mem_free,
            "gpu_utilization_percent": gpu_util,
        }

        append_sample(output_file, row)
        time.sleep(interval)


def main() -> int:
    """Program entry point."""
    args = parse_args()

    if args.interval <= 0:
        print("ERROR: --interval must be positive.", file=sys.stderr)
        return 2

    if not psutil.pid_exists(args.pid):
        print(f"ERROR: PID {args.pid} does not exist.", file=sys.stderr)
        return 2

    try:
        return monitor(
            pid=args.pid,
            output_file=args.output,
            interval=args.interval,
            append=args.append,
        )
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(f"ERROR: resource monitor failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
