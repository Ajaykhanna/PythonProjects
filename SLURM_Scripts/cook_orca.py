#!/usr/bin/env python3
"""
ORCA SLURM Job Submission Script Generator.

This script generates SLURM job submission scripts for running ORCA
computational chemistry calculations. It handles resource configuration,
environment setup, scratch directory management, and optional job submission.

Developer: Ajay Khanna
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
from jinja2 import Template

# Configuration for ORCA and SLURM
CONFIG = {
    "scratch_root": "/tmp/akhanna2/scratch/ORCA_SCR",
    "partitions": {
        "general": {"max_time": "10:00:00", "qos": None},
        "long": {"max_time": "120:00:00", "qos": "long"},
    },
    "openmpi": {
        "module": "openmpi/4.1.6-gcc_13.2.0",
        "bin_path": "/4.1.6-gcc_13.2.0/bin",
        "lib_path": "/4.1.6-gcc_13.2.0/lib",
    },
    "orca_path": "/projects/ORCA/orca_6_0_1",
}

# SLURM script template for ORCA jobs
SLURM_TEMPLATE = """#!/bin/bash
#SBATCH --partition={{ partition }}
{% if qos %}#SBATCH --qos={{ qos }}{% endif %}
#SBATCH --time={{ time }}
#SBATCH --nodes={{ nodes }}
#SBATCH --ntasks={{ ntasks }}
#SBATCH --mem={{ mem }}GB
#SBATCH --job-name={{ jobname }}
#SBATCH --error={{ jobname }}.err
#SBATCH --output={{ jobname }}.qlog

# Load necessary modules and set environment variables
module load {{ openmpi.module }}
export PATH={{ openmpi.bin_path }}:{{ orca_path }}:$PATH
export LD_LIBRARY_PATH={{ openmpi.lib_path }}:{{ orca_path }}:$LD_LIBRARY_PATH
export ORCA={{ orca_path }}

# Log job initialization details
echo "Job ID: $SLURM_JOBID" >> {{ jobname }}.qlog
echo "Working directory: $PWD" >> {{ jobname }}.qlog
echo "Job started at $(date)" >> {{ jobname }}.qlog

# Set up scratch directory
MY_SCRATCH="{{ scratch_root }}/$SLURM_JOBID"
mkdir -p $MY_SCRATCH
cp -r $PWD/* $MY_SCRATCH
echo "Scratch directory: $MY_SCRATCH" >> {{ jobname }}.qlog

# Memory monitoring background process
(
  while true; do
    if scontrol show job $SLURM_JOBID | grep -q "JobState=RUNNING"; then
        mem_used=$(free -m | awk 'NR==2 {print $3}')
        mem_total=$(free -m | awk 'NR==2 {print $2}')
        mem_percent=$(echo "scale=2; ($mem_used/$mem_total)*100" | bc)
        echo "$(date) - Memory: ${mem_used}MB/${mem_total}MB (${mem_percent}%)" >> {{ jobname }}.qlog
        sleep 60
    else
        break
    fi
  done
) &

BG_PID=$!
trap "kill $BG_PID; exit" SIGINT

# Execute ORCA calculation
echo "Starting ORCA calculation at $(date)" >> {{ jobname }}.qlog
$ORCA/orca $MY_SCRATCH/{{ input_file }} > $MY_SCRATCH/{{ output_file }}

# Allow cleanup and copy results back
sleep 10
echo "Copying results from scratch at $(date)" >> {{ jobname }}.qlog
cp -r $MY_SCRATCH/* $PWD/

# Cleanup processes and directories
kill $BG_PID
rm -rf $MY_SCRATCH

# Final job completion logging
echo "Job completed at $(date)" >> {{ jobname }}.qlog
echo "Scratch directory removed successfully" >> {{ jobname }}.qlog
echo "Success or Failed, Still Buy The Developer A Beer" >> {{ jobname }}.qlog
"""


def create_slurm_script(args) -> Optional[str]:
    """Generate a SLURM submission script using the ORCA template."""
    if args.filename != "dummy.inp" and not Path(args.filename).exists():
        print(f"Error: Input file '{args.filename}' not found.")
        return None

    jobname = Path(args.filename).stem
    partition_config = CONFIG["partitions"].get(
        args.partition, CONFIG["partitions"]["general"]
    )

    context = {
        "input_file": Path(args.filename).name,
        "output_file": f"{Path(args.filename).stem}.log",
        "jobname": jobname,
        "nodes": args.nodes,
        "ntasks": args.ntasks,
        "mem": args.mem,
        "time": args.time or partition_config["max_time"],
        "partition": args.partition,
        "qos": partition_config["qos"],
        "scratch_root": CONFIG["scratch_root"],
        "openmpi": CONFIG["openmpi"],
        "orca_path": CONFIG["orca_path"],
    }

    template = Template(SLURM_TEMPLATE)
    return template.render(**context)


def main():
    """Parse command line arguments and generate/submit SLURM script."""
    parser = argparse.ArgumentParser(
        description="Generate and submit SLURM jobs for ORCA calculations.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-f",
        "--filename",
        default="dummy.inp",
        help="ORCA input file (use 'dummy.inp' for template)",
    )
    parser.add_argument(
        "-n", "--nodes", type=int, default=1, help="Number of compute nodes"
    )
    parser.add_argument(
        "-np",
        "--ntasks",
        type=int,
        default=8,
        help="Number of parallel tasks (MPI processes)",
    )
    parser.add_argument(
        "-m", "--mem", type=int, default=100, help="Memory per node in GB"
    )
    parser.add_argument(
        "-t", "--time", help="Wall time limit (HH:MM:SS or DD-HH:MM:SS)"
    )
    parser.add_argument(
        "-p",
        "--partition",
        default="general",
        choices=CONFIG["partitions"].keys(),
        help="SLURM partition for submission",
    )
    parser.add_argument(
        "--submit", action="store_true", help="Immediately submit generated job"
    )

    args = parser.parse_args()

    if script_content := create_slurm_script(args):
        script_name = f"submit_{Path(args.filename).stem}.sbatch"
        Path(script_name).write_text(script_content)
        print(f"Generated SLURM script: {script_name}")

        if args.submit:
            try:
                result = subprocess.run(
                    ["sbatch", script_name], check=True, capture_output=True, text=True
                )
                job_id = result.stdout.strip().split()[-1]
                print(
                    f"Job {job_id} submitted successfully\n"
                    f"Output log: {Path(args.filename).stem}.log\n"
                    f"Job logs: {Path(args.filename).stem}.qlog"
                )
            except subprocess.CalledProcessError as e:
                print(f"Submission failed: {e.stderr}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
