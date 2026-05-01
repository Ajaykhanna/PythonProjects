#!/usr/bin/env python3
"""
resource_report.py

Generate a human-readable resource consumption report from a resource monitor CSV.

This script is intended to run after a SLURM training job finishes. It reads the
CSV produced by resource_monitor.py and writes a text report containing:

    - Job configuration
    - Duration
    - CPU allocated core-hours
    - Estimated CPU core-hours actually used
    - GPU allocated hours
    - Estimated GPU utilization-weighted hours
    - Average and peak process memory
    - RAM GB-hours
    - Average and peak node memory
    - Peak GPU VRAM usage
    - Storage created during the job
    - Storage-hours
    - Resource request recommendations

The report format intentionally resembles the user's earlier
resource_consumption_report_SLURMID.txt format.

Notes
-----
CPU core-hours:
    Two values are reported:
      1. Allocated CPU core-hours = duration_hours * allocated CPU cores
      2. Estimated used CPU core-hours = integral(process_cpu_percent / 100)

GPU hours:
    Two values are reported:
      1. Allocated GPU hours = duration_hours * allocated GPU count
      2. Estimated utilized GPU hours = allocated GPU hours * mean GPU utilization

Memory:
    Process memory comes from the monitored process tree RSS.
    System memory comes from psutil.virtual_memory() on the node.

Storage:
    Storage created is computed as:
        storage_after_bytes - storage_before_bytes

    If the directory had pre-existing files, this reports net storage growth,
    not necessarily all files produced by the job.

Developer Information
---------------
  __developer__: "Ajay Khanna"
  __place__: "LANL"
  __date__: "May-01-2026"
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate SLURM resource consumption report from monitor CSV."
    )

    parser.add_argument("--csv", required=True, type=Path, help="Resource monitor CSV.")
    parser.add_argument(
        "--output", required=True, type=Path, help="Output report path."
    )

    parser.add_argument("--job-id", required=True, help="SLURM job ID.")
    parser.add_argument("--job-name", default="N/A", help="SLURM job name.")
    parser.add_argument("--node", default="N/A", help="Node name.")

    parser.add_argument(
        "--start-epoch", required=True, type=int, help="Job start epoch seconds."
    )
    parser.add_argument(
        "--end-epoch", required=True, type=int, help="Job end epoch seconds."
    )

    parser.add_argument(
        "--cpu-cores", required=True, type=float, help="Allocated CPU cores."
    )
    parser.add_argument(
        "--gpu-count", required=True, type=float, help="Allocated GPU count."
    )
    parser.add_argument(
        "--memory-limit-mb",
        default="N/A",
        help="SLURM memory limit in MB, or N/A.",
    )

    parser.add_argument(
        "--storage-path", required=True, help="Measured storage directory."
    )
    parser.add_argument("--storage-before-bytes", required=True, type=int)
    parser.add_argument("--storage-after-bytes", required=True, type=int)
    parser.add_argument("--file-count-before", required=True, type=int)
    parser.add_argument("--file-count-after", required=True, type=int)

    parser.add_argument("--batch-size", default="N/A")
    parser.add_argument("--total-configurations", default="N/A")
    parser.add_argument("--atoms-per-molecule", default="N/A")
    parser.add_argument("--electronic-states", default="N/A")
    parser.add_argument("--exit-status", default="N/A")

    return parser.parse_args()


def parse_float(value: str | None) -> float | None:
    """Safely parse a float from a CSV field."""
    if value is None:
        return None

    value = str(value).strip()

    if not value or value.upper() == "N/A":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def parse_timestamp(value: str) -> datetime | None:
    """Parse ISO-like timestamp from monitor CSV."""
    if not value:
        return None

    value = value.strip()

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def parse_semicolon_floats(value: str | None) -> list[float]:
    """
    Parse semicolon-separated numeric values.

    Example:
        "1200;3400;2100" -> [1200.0, 3400.0, 2100.0]
    """
    if value is None:
        return []

    value = str(value).strip()

    if not value or value.upper() == "N/A":
        return []

    result: list[float] = []

    for part in value.split(";"):
        part = part.strip()
        if not part or part.upper() == "N/A":
            continue
        try:
            result.append(float(part))
        except ValueError:
            continue

    return result


def bytes_to_gb(num_bytes: int | float) -> float:
    """Convert bytes to decimal GB."""
    return float(num_bytes) / 1_000_000_000.0


def mb_to_gb(num_mb: float) -> float:
    """Convert MiB-like MB value to GiB-like GB value using 1024."""
    return num_mb / 1024.0


def fmt_seconds(seconds: int) -> str:
    """Format seconds as Hh Mm Ss."""
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"


def mean_or_zero(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return statistics.mean(values)


def max_or_zero(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return max(values)


def ceil_to_int(value: float) -> int:
    """Return a conservative integer recommendation."""
    if value <= 0:
        return 0
    return int(math.ceil(value))


def read_monitor_csv(csv_path: Path) -> dict[str, object]:
    """
    Read resource monitor CSV and compute summary metrics.

    Returns a dictionary of lists and aggregate values used by the report writer.
    """
    timestamps: list[datetime] = []
    process_cpu_percent: list[float] = []
    process_memory_mb: list[float] = []
    system_memory_used_mb: list[float] = []
    system_memory_percent: list[float] = []
    gpu_memory_max_per_sample_mb: list[float] = []
    gpu_util_mean_per_sample_percent: list[float] = []

    if not csv_path.exists():
        raise FileNotFoundError(f"Resource CSV not found: {csv_path}")

    with csv_path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)

        for row in reader:
            timestamp = parse_timestamp(row.get("timestamp", ""))
            if timestamp is not None:
                timestamps.append(timestamp)

            cpu = parse_float(row.get("process_cpu_percent"))
            if cpu is not None:
                process_cpu_percent.append(cpu)

            memory = parse_float(row.get("process_memory_mb"))
            if memory is not None:
                process_memory_mb.append(memory)

            sys_mem = parse_float(row.get("system_memory_used_mb"))
            if sys_mem is not None:
                system_memory_used_mb.append(sys_mem)

            sys_mem_pct = parse_float(row.get("system_memory_percent"))
            if sys_mem_pct is not None:
                system_memory_percent.append(sys_mem_pct)

            gpu_mem_values = parse_semicolon_floats(row.get("gpu_memory_used_mb"))
            if gpu_mem_values:
                gpu_memory_max_per_sample_mb.append(max(gpu_mem_values))

            gpu_util_values = parse_semicolon_floats(row.get("gpu_utilization_percent"))
            if gpu_util_values:
                gpu_util_mean_per_sample_percent.append(mean_or_zero(gpu_util_values))

    return {
        "timestamps": timestamps,
        "process_cpu_percent": process_cpu_percent,
        "process_memory_mb": process_memory_mb,
        "system_memory_used_mb": system_memory_used_mb,
        "system_memory_percent": system_memory_percent,
        "gpu_memory_max_per_sample_mb": gpu_memory_max_per_sample_mb,
        "gpu_util_mean_per_sample_percent": gpu_util_mean_per_sample_percent,
        "sample_count": len(timestamps),
    }


def write_report(args: argparse.Namespace, metrics: dict[str, object]) -> None:
    """Write the resource consumption report."""
    start_dt = datetime.fromtimestamp(args.start_epoch)
    end_dt = datetime.fromtimestamp(args.end_epoch)

    duration_seconds = max(0, args.end_epoch - args.start_epoch)
    duration_hours = duration_seconds / 3600.0

    cpu_cores = float(args.cpu_cores)
    gpu_count = float(args.gpu_count)

    allocated_cpu_core_hours = duration_hours * cpu_cores
    allocated_gpu_hours = duration_hours * gpu_count

    process_cpu_percent = metrics["process_cpu_percent"]
    process_memory_mb = metrics["process_memory_mb"]
    system_memory_used_mb = metrics["system_memory_used_mb"]
    system_memory_percent = metrics["system_memory_percent"]
    gpu_memory_max_per_sample_mb = metrics["gpu_memory_max_per_sample_mb"]
    gpu_util_mean_per_sample_percent = metrics["gpu_util_mean_per_sample_percent"]

    assert isinstance(process_cpu_percent, list)
    assert isinstance(process_memory_mb, list)
    assert isinstance(system_memory_used_mb, list)
    assert isinstance(system_memory_percent, list)
    assert isinstance(gpu_memory_max_per_sample_mb, list)
    assert isinstance(gpu_util_mean_per_sample_percent, list)

    avg_cpu_percent = mean_or_zero(process_cpu_percent)
    peak_cpu_percent = max_or_zero(process_cpu_percent)

    # This is an estimate using average CPU percentage over the job duration.
    estimated_used_cpu_core_hours = duration_hours * (avg_cpu_percent / 100.0)

    avg_process_memory_mb = mean_or_zero(process_memory_mb)
    peak_process_memory_mb = max_or_zero(process_memory_mb)
    avg_process_memory_gb = mb_to_gb(avg_process_memory_mb)
    peak_process_memory_gb = mb_to_gb(peak_process_memory_mb)

    process_memory_gb_hours = avg_process_memory_gb * duration_hours

    avg_system_memory_mb = mean_or_zero(system_memory_used_mb)
    peak_system_memory_mb = max_or_zero(system_memory_used_mb)
    avg_system_memory_gb = mb_to_gb(avg_system_memory_mb)
    peak_system_memory_gb = mb_to_gb(peak_system_memory_mb)

    avg_system_memory_percent = mean_or_zero(system_memory_percent)
    peak_system_memory_percent = max_or_zero(system_memory_percent)

    avg_gpu_util_percent = mean_or_zero(gpu_util_mean_per_sample_percent)
    peak_gpu_util_percent = max_or_zero(gpu_util_mean_per_sample_percent)
    estimated_utilized_gpu_hours = allocated_gpu_hours * (avg_gpu_util_percent / 100.0)

    peak_gpu_memory_mb = max_or_zero(gpu_memory_max_per_sample_mb)
    peak_gpu_memory_gb = mb_to_gb(peak_gpu_memory_mb)

    recommended_memory_mb = peak_process_memory_mb * 1.20
    recommended_memory_gb = mb_to_gb(recommended_memory_mb)

    recommended_gpu_memory_mb = peak_gpu_memory_mb * 1.20
    recommended_gpu_memory_gb = mb_to_gb(recommended_gpu_memory_mb)

    storage_before_gb = bytes_to_gb(args.storage_before_bytes)
    storage_after_gb = bytes_to_gb(args.storage_after_bytes)
    storage_created_bytes = max(0, args.storage_after_bytes - args.storage_before_bytes)
    storage_created_gb = bytes_to_gb(storage_created_bytes)

    files_created = max(0, args.file_count_after - args.file_count_before)

    avg_file_size_mb = 0.0
    if files_created > 0:
        avg_file_size_mb = (storage_created_bytes / files_created) / 1_000_000.0

    storage_hours = storage_created_gb * duration_hours

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w") as f:
        f.write(
            "================================================================================\n"
        )
        f.write(f"RESOURCE CONSUMPTION REPORT - {args.job_name}\n")
        f.write(
            "================================================================================\n"
        )
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Job ID: {args.job_id}\n")
        f.write(f"Exit Status: {args.exit_status}\n")
        f.write("\n")

        f.write("JOB CONFIGURATION\n")
        f.write(
            "--------------------------------------------------------------------------------\n"
        )
        f.write(
            f"  Total Duration:          {fmt_seconds(duration_seconds)} ({duration_seconds} seconds)\n"
        )
        f.write(
            f"  Start Time:              {start_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        f.write(f"  End Time:                {end_dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"  Node:                    {args.node}\n")
        f.write(f"  CPU Cores Allocated:     {cpu_cores:g}\n")
        f.write(f"  GPU Count Allocated:     {gpu_count:g}\n")
        f.write(f"  Batch Size:              {args.batch_size}\n")
        f.write(f"  Total Configurations:    {args.total_configurations}\n")
        f.write(f"  Atoms per Molecule:      {args.atoms_per_molecule}\n")
        f.write(f"  Electronic States:       {args.electronic_states}\n")
        f.write(f"  Monitor Samples:         {metrics['sample_count']}\n")
        f.write("\n")

        f.write("CPU CORE-HOUR ANALYSIS\n")
        f.write(
            "--------------------------------------------------------------------------------\n"
        )
        f.write("  Formula:                 (Duration in hours) x (CPU cores)\n")
        f.write(
            f"  Calculation:             ({duration_seconds} sec / 3600) x {cpu_cores:g} cores\n"
        )
        f.write(
            f"  CPU Core-Hours:          {allocated_cpu_core_hours:.3f} core-hours\n"
        )
        f.write(f"  Mean CPU Utilization:    {avg_cpu_percent:.1f}%\n")
        f.write(f"  Peak CPU Utilization:    {peak_cpu_percent:.1f}%\n")
        f.write(
            f"  Est. Used Core-Hours:    {estimated_used_cpu_core_hours:.3f} core-hours\n"
        )
        f.write(
            "  Note:                    CPU Core-Hours above are allocated core-hours\n"
        )
        f.write("\n")

        f.write("GPU CORE-HOUR ANALYSIS\n")
        f.write(
            "--------------------------------------------------------------------------------\n"
        )
        f.write("  Formula:                 (Duration in hours) x (GPU count)\n")
        f.write(
            f"  Calculation:             ({duration_seconds} sec / 3600) x {gpu_count:g} GPUs\n"
        )
        f.write(f"  GPU Core-Hours:          {allocated_gpu_hours:.3f} core-hours\n")
        f.write(f"  Mean GPU Utilization:    {avg_gpu_util_percent:.1f}%\n")
        f.write(f"  Peak GPU Utilization:    {peak_gpu_util_percent:.1f}%\n")
        f.write(
            f"  Est. Used GPU-Hours:     {estimated_utilized_gpu_hours:.3f} GPU-hours\n"
        )
        f.write(
            "  Note:                    Actual GPU utilization may be lower than allocation\n"
        )
        f.write("\n")

        f.write("MEMORY CONSUMPTION\n")
        f.write(
            "--------------------------------------------------------------------------------\n"
        )
        f.write(
            f"  Process Average Memory:  {avg_process_memory_mb:.1f} MB ({avg_process_memory_gb:.2f} GB)\n"
        )
        f.write(
            f"  Process Peak Memory:     {peak_process_memory_mb:.1f} MB ({peak_process_memory_gb:.2f} GB)\n"
        )
        f.write(f"  Process Avg x Duration:  {process_memory_gb_hours:.3f} GB-hours\n")
        f.write("\n")
        f.write(
            f"  System Average Usage:    {avg_system_memory_mb:.1f} MB ({avg_system_memory_gb:.2f} GB)\n"
        )
        f.write(
            f"  System Peak Usage:       {peak_system_memory_mb:.1f} MB ({peak_system_memory_gb:.2f} GB)\n"
        )
        f.write(f"  System Avg Usage %:      {avg_system_memory_percent:.1f}%\n")
        f.write(f"  System Peak Usage %:     {peak_system_memory_percent:.1f}%\n")
        f.write(f"  System Memory Limit:     {args.memory_limit_mb}\n")
        f.write("\n")
        f.write(
            f"  Peak GPU VRAM Used:      {peak_gpu_memory_mb:.1f} MB ({peak_gpu_memory_gb:.2f} GB)\n"
        )
        f.write(
            f"  GPU VRAM +20%:           {recommended_gpu_memory_mb:.1f} MB ({recommended_gpu_memory_gb:.2f} GB)\n"
        )
        f.write("\n")

        f.write("STORAGE CONSUMPTION\n")
        f.write(
            "--------------------------------------------------------------------------------\n"
        )
        f.write(f"  Storage Path:            {args.storage_path}\n")
        f.write(f"  Files Before Job:        {args.file_count_before}\n")
        f.write(f"  Files After Job:         {args.file_count_after}\n")
        f.write(f"  Total Output Files:      {files_created}\n")
        f.write(f"  Size Before Job:         {storage_before_gb:.3f} GB\n")
        f.write(f"  Size After Job:          {storage_after_gb:.3f} GB\n")
        f.write(f"  Total Output Size:       {storage_created_gb:.3f} GB\n")
        f.write(f"  Average File Size:       {avg_file_size_mb:.1f} MB\n")
        f.write("\n")
        f.write(f"  Storage-Hours:           {storage_hours:.3f} GB-hours\n")
        f.write("  (Storage footprint x job duration)\n")
        f.write("\n")

        f.write("RESOURCE REQUEST RECOMMENDATIONS\n")
        f.write(
            "--------------------------------------------------------------------------------\n"
        )
        f.write(f"  Recommended CPUs:        {ceil_to_int(cpu_cores)} cores ")
        f.write(
            f"(allocated {allocated_cpu_core_hours:.3f} core-hours; est. used {estimated_used_cpu_core_hours:.3f})\n"
        )
        f.write(f"  Recommended GPUs:        {ceil_to_int(gpu_count)} GPUs ")
        f.write(
            f"(allocated {allocated_gpu_hours:.3f} GPU-hours; est. used {estimated_utilized_gpu_hours:.3f})\n"
        )
        f.write(f"  Recommended --mem:       {math.ceil(recommended_memory_gb)}G ")
        f.write(f"(peak {peak_process_memory_gb:.2f} GB + 20%)\n")

        if peak_gpu_memory_mb > 0:
            f.write(
                f"  Recommended GPU VRAM:    >= {recommended_gpu_memory_gb:.2f} GB "
            )
            f.write("(peak GPU VRAM + 20%)\n")
        else:
            f.write("  Recommended GPU VRAM:    N/A\n")

        f.write("\n")
        f.write("REPORT FILES\n")
        f.write(
            "--------------------------------------------------------------------------------\n"
        )
        f.write(f"  Resource CSV:            {args.csv}\n")
        f.write(f"  Resource Report:         {args.output}\n")
        f.write(
            "================================================================================\n"
        )

    print(f"Resource consumption report written to: {args.output}")


def main() -> int:
    args = parse_args()
    metrics = read_monitor_csv(args.csv)
    write_report(args, metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
