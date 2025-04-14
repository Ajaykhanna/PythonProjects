#!/usr/bin/env python3
"""
Gaussian16 SLURM Job Submission Script Generator.

This script generates SLURM job submission scripts for running Gaussian16
computational chemistry calculations. It handles configuration of resources,
environment setup, and optional job submission.

Developer: Ajay Khanna
Date: Dec.12.2024
"""

import argparse
import os
import re
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, Template

# Configuration could be loaded from a YAML file
CONFIG = {
    "scratch_root": "/tmp/akhanna2/GAUSSIAN_SCR",
    "g16root": "/Gaussian/g16A03",
    "partitions": {
        "general": {"max_time": "10:00:00", "qos": "Normal"},
        "ml4chem": {"max_time": "10:00:00", "qos": "Normal"},
        "general": {"max_time": "48:00:00", "qos": "long"},
    },
}

# Template stored as a separate file or as a string
SLURM_TEMPLATE = """#!/bin/csh
#SBATCH --partition={{ partition }}
{% if qos %}#SBATCH --qos={{ qos }}{% endif %}
#SBATCH --time={{ time }}
#SBATCH --nodes={{ nodes }}
#SBATCH --ntasks={{ ntasks }}
#SBATCH --mem={{ mem }}GB
#SBATCH --job-name={{ jobname }}
#SBATCH --error={{ jobname }}.err
#SBATCH --output={{ jobname }}.qlog

# Set up scratch directory
setenv MY_SCRATCH {{ scratch_root }}/${SLURM_JOBID}/
mkdir -p ${MY_SCRATCH}
setenv GAUSS_SCRDIR ${MY_SCRATCH}

# Set up Gaussian environment
setenv g16root {{ g16root }}
source ${g16root}/g16/bsd/g16.login

# Log job information
echo "Job started at `date`" > {{ jobname }}.qlog
echo "Job ID: ${SLURM_JOBID}" >> {{ jobname }}.qlog
echo "Working directory: ${PWD}" >> {{ jobname }}.qlog
echo "Scratch directory: ${GAUSS_SCRDIR}" >> {{ jobname }}.qlog
echo "Memory requested: {{ mem }}GB" >> {{ jobname }}.qlog
echo "CPUs requested: {{ ntasks }}" >> {{ jobname }}.qlog

# Run Gaussian calculation
g16 -m={{ mem }}GB -p={{ ntasks }} < {{ input_file }} > {{ output_file }}

# Clean up scratch directory
rm -rf ${MY_SCRATCH}
"""


def create_slurm_script(args) -> Optional[str]:
    """Generate a SLURM submission script using a template."""
    # Validate inputs
    if args.filename != "dummy.com" and not Path(args.filename).exists():
        print(f"Error: Input file '{args.filename}' not found.")
        return None

    # Create template context
    jobname = Path(args.filename).stem
    partition_config = CONFIG["partitions"].get(
        args.partition, CONFIG["partitions"]["general"]
    )

    context = {
        "input_file": args.filename,
        "output_file": f"{Path(args.filename).stem}.log",
        "jobname": jobname,
        "nodes": args.nodes,
        "ntasks": args.ntasks,
        "mem": args.mem,
        "time": args.time or partition_config["max_time"],
        "partition": args.partition,
        "qos": partition_config["qos"],
        "scratch_root": CONFIG["scratch_root"],
        "g16root": CONFIG["g16root"],
    }

    # Render template
    template = Template(SLURM_TEMPLATE)
    return template.render(**context)


def main():
    """Parse command line arguments and generate/submit SLURM script."""
    parser = argparse.ArgumentParser(
        description="Generate and submit SLURM jobs for Gaussian16 calculations.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Define command-line arguments with more options
    parser.add_argument(
        "-f",
        "--filename",
        default="dummy.com",
        help="Gaussian input file (use 'dummy.com' for template)",
    )
    parser.add_argument("-n", "--nodes", type=int, default=1, help="Number of nodes")
    parser.add_argument(
        "-np", "--ntasks", type=int, default=4, help="Number of tasks (cores)"
    )
    parser.add_argument(
        "-m", "--mem", type=int, default=2, help="Memory per node in GB"
    )
    parser.add_argument(
        "-t",
        "--time",
        help="Wall time limit (HH:MM:SS format, defaults to partition max)",
    )
    parser.add_argument(
        "-p",
        "--partition",
        default="general",
        choices=CONFIG["partitions"].keys(),
        help="SLURM partition to submit to",
    )
    parser.add_argument(
        "--submit", action="store_true", help="Submit job after generation"
    )

    # Parse arguments
    args = parser.parse_args()

    # Generate script
    script_content = create_slurm_script(args)
    if not script_content:
        sys.exit(1)

    # Write to file
    script_name = f"submit_{Path(args.filename).stem}.sbatch"
    Path(script_name).write_text(script_content)
    print(f"Generated SLURM script: {script_name}")

    # Submit job if requested
    if args.submit:
        try:
            result = subprocess.run(
                ["sbatch", script_name],
                check=True,
                capture_output=True,
                text=True,
            )
            job_id = result.stdout.strip().split()[-1]
            print(
                f"""
Job successfully submitted:
- Job ID: {job_id}
- Input file: {args.filename}
- Log file: {os.path.splitext(args.filename)[0]}.log
- Qlog file: {os.path.splitext(args.filename)[0]}.qlog"""
            )
        except subprocess.CalledProcessError as e:
            print(f"Submission failed: {e.stderr}")
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("Job not submitted (use --submit to queue)")


if __name__ == "__main__":
    main()
