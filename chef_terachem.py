#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chef-TeraChem: A Python script to generate TeraChem input files.

This script prompts the user for calculation parameters and generates
an appropriate TeraChem input file (.in) for various quantum chemistry
calculations, including options for ground state, excited state,
energy, optimization, frequency, and implicit solvent effects (COSMO).
"""

import sys
from typing import Dict, Optional, Any, Tuple

# --- Constants and Configuration ---

__version__ = "1.1.0"  # Refactored version
__author__ = "Ajay Khanna (Original), Refactored by AI"
__date__ = "Oct.10.2020 (Original), April 21, 2025 (Refactored)"
__lab__ = "Dr. Isborb's Lab | UC-Merced"

# Mapping of calculation type codes to descriptive names and run types
CALC_TYPE_MAP: Dict[int, Tuple[str, str]] = {
    0: ("gs_energy", "energy"),
    1: ("gs_opt", "minimize"),
    2: ("gs_freq", "frequencies"),
    3: ("ex_energy", "energy"),
    4: ("ex_opt", "minimize"),
    5: ("ex_freq", "frequencies"),
}
# Calculation types requiring excited state ('cis') options
EXCITED_STATE_CALCS: Tuple[int, ...] = (3, 4, 5)

# Solvent dielectric constants (Source: Gaussian website, Oct 10, 2020)
# Moved here for clarity, could be in a separate JSON/YAML/module
SOLVENT_DIELECTRICS: Dict[str, float] = {
    "water": 78.3553,
    "acetonitrile": 35.688,
    "methanol": 32.613,
    "ethanol": 24.852,
    "isoquinoline": 11.00,
    "quinoline": 9.16,
    "chloroform": 4.7113,
    "diethylether": 4.2400,
    "dichloromethane": 8.93,
    "dichloroethane": 10.125,
    "carbontetrachloride": 2.2280,
    "benzene": 2.2706,
    "toluene": 2.3741,
    "chlorobenzene": 5.6968,
    "nitromethane": 36.562,
    "heptane": 1.9113,
    "cyclohexane": 2.0165,
    "aniline": 6.8882,
    "acetone": 20.493,
    "tetrahydrofuran": 7.4257,
    "dimethylsulfoxide": 46.826,
    "argon": 1.430,
    "krypton": 1.519,
    "xenon": 1.706,
    "n-octanol": 9.8629,
    "1,1,1-trichloroethane": 7.0826,
    "1,1,2-trichloroethane": 7.1937,
    "1,2,4-trimethylbenzene": 2.3653,
    "1,2-dibromoethane": 4.9313,
    "1,2-ethanediol": 40.245,
    "1,4-dioxane": 2.2099,
    "1-bromo-2-methylpropane": 7.7792,
    "1-bromooctane": 5.0244,
    "1-bromopentane": 6.269,
    "1-bromopropane": 8.0496,
    "1-butanol": 17.332,
    "1-chlorohexane": 5.9491,
    "1-chloropentane": 6.5022,
    "1-chloropropane": 8.3548,
    "1-decanol": 7.5305,
    "1-fluorooctane": 3.89,
    "1-heptanol": 11.321,
    "1-hexanol": 12.51,
    "1-hexene": 2.0717,
    "1-hexyne": 2.615,
    "1-iodobutane": 6.173,
    "1-iodohexadecane": 3.5338,
    "1-iodopentane": 5.6973,
    "1-iodopropane": 6.9626,
    "1-nitropropane": 23.73,
    "1-nonanol": 8.5991,
    "1-pentanol": 15.13,
    "1-pentene": 1.9905,
    "1-propanol": 20.524,
    "2,2,2-trifluoroethanol": 26.726,
    "2,2,4-trimethylpentane": 1.9358,
    "2,4-dimethylpentane": 1.8939,
    "2,4-dimethylpyridine": 9.4176,
    "2,6-dimethylpyridine": 7.1735,
    "2-bromopropane": 9.3610,
    "2-butanol": 15.944,
    "2-chlorobutane": 8.3930,
    "2-heptanone": 11.658,
    "2-hexanone": 14.136,
    "2-methoxyethanol": 17.2,
    "2-methyl-1-propanol": 16.777,
    "2-methyl-2-propanol": 12.47,
    "2-methylpentane": 1.89,
    "2-methylpyridine": 9.9533,
    "2-nitropropane": 25.654,
    "2-octanone": 9.4678,
    "2-pentanone": 15.200,
    "2-propanol": 19.264,
    "2-propen-1-ol": 19.011,
    "3-methylpyridine": 11.645,
    "3-pentanone": 16.78,
    "4-heptanone": 12.257,
    "4-methyl-2-pentanone": 12.887,
    "4-methylpyridine": 11.957,
    "5-nonanone": 10.6,
    "aceticacid": 6.2528,
    "acetophenone": 17.44,
    "a-chlorotoluene": 6.7175,
    "anisole": 4.2247,
    "benzaldehyde": 18.220,
    "benzonitrile": 25.592,
    "benzylalcohol": 12.457,
    "bromobenzene": 5.3954,
    "bromoethane": 9.01,
    "bromoform": 4.2488,
    "butanal": 13.45,
    "butanoicacid": 2.9931,
    "butanone": 18.246,
    "butanonitrile": 24.291,
    "butylamine": 4.6178,
    "butylethanoate": 4.9941,
    "carbondisulfide": 2.6105,
    "cis-1,2-dimethylcyclohexane": 2.06,
    "cis-decalin": 2.2139,
    "cyclohexanone": 15.619,
    "cyclopentane": 1.9608,
    "cyclopentanol": 16.989,
    "cyclopentanone": 13.58,
    "decalin-mixture": 2.196,
    "dibromomethane": 7.2273,
    "dibutylether": 3.0473,
    "diethylamine": 3.5766,
    "diethylsulfide": 5.723,
    "diiodomethane": 5.32,
    "diisopropylether": 3.38,
    "dimethyldisulfide": 9.6,
    "diphenylether": 3.73,
    "dipropylamine": 2.9112,
    "e-1,2-dichloroethene": 2.14,
    "e-2-pentene": 2.051,
    "ethanethiol": 6.667,
    "ethylbenzene": 2.4339,
    "ethylethanoate": 5.9867,
    "ethylmethanoate": 8.3310,
    "ethylphenylether": 4.1797,
    "fluorobenzene": 5.42,
    "formamide": 108.94,
    "formicacid": 51.1,
    "hexanoicacid": 2.6,
    "iodobenzene": 4.5470,
    "iodoethane": 7.6177,
    "iodomethane": 6.8650,
    "isopropylbenzene": 2.3712,
    "m-cresol": 12.44,
    "mesitylene": 2.2650,
    "methylbenzoate": 6.7367,
    "methylbutanoate": 5.5607,
    "methylcyclohexane": 2.024,
    "methylethanoate": 6.8615,
    "methylmethanoate": 8.8377,
    "methylpropanoate": 6.0777,
    "m-xylene": 2.3478,
    "n-butylbenzene": 2.36,
    "n-decane": 1.9846,
    "n-dodecane": 2.0060,
    "n-hexadecane": 2.0402,
    "n-hexane": 1.8819,
    "nitrobenzene": 34.809,
    "nitroethane": 28.29,
    "n-methylaniline": 5.9600,
    "n-methylformamide-mixture": 181.56,
    "n,n-dimethylacetamide": 37.781,
    "n,n-dimethylformamide": 37.219,
    "n-nonane": 1.9605,
    "n-octane": 1.9406,
    "n-pentadecane": 2.0333,
    "n-pentane": 1.8371,
    "n-undecane": 1.9910,
    "o-chlorotoluene": 4.6331,
    "o-cresol": 6.76,
    "o-dichlorobenzene": 9.9949,
    "o-nitrotoluene": 25.669,
    "o-xylene": 2.5454,
    "pentanal": 10.0,
    "pentanoicacid": 2.6924,
    "pentylamine": 4.2010,
    "pentylethanoate": 4.7297,
    "perfluorobenzene": 2.029,
    "p-isopropyltoluene": 2.2322,
    "propanal": 18.5,
    "propanoicacid": 3.44,
    "propanonitrile": 29.324,
    "propylamine": 4.9912,
    "propylethanoate": 5.5205,
    "p-xylene": 2.2705,
    "pyridine": 12.978,
    "sec-butylbenzene": 2.3446,
    "tert-butylbenzene": 2.3447,
    "tetrachloroethene": 2.268,
    "tetrahydrothiophene-s,s-dioxide": 43.962,
    "tetralin": 2.771,
    "thiophene": 2.7270,
    "thiophenol": 4.2728,
    "trans-decalin": 2.1781,
    "tributylphosphate": 8.1781,
    "trichloroethene": 3.422,
    "triethylamine": 2.3832,
    "xylene-mixture": 2.3879,
    "z-1,2-dichloroethene": 9.2,
}

DEFAULT_GPUS: int = 4
DEFAULT_CIS_NUMSTATES: int = 6
DEFAULT_CIS_GUESVECS_FACTOR: int = 2  # cisguessvecs = factor * cisnumstates
DEFAULT_CISTARGET: int = 1

# --- Helper Functions ---


def print_header() -> None:
    """Prints the script header and developer information."""
    print("*********| Chef-TeraChem | **********")
    print(" A python script to create on-demand TeraChem input files.")
    print(f" Version: {__version__} (Refactored)")
    print(f" Based on original script by: {__author__.split('(')[0].strip()}")
    print(f" Original Date: {__date__.split(',')[0].strip()}")
    print(f" Lab: {__lab__}")
    print("-" * 40)
    print("Current Calculation Options:")
    for code, (name, _) in CALC_TYPE_MAP.items():
        state = "Ground State" if "gs" in name else "Excited State"
        calc = name.split("_")[1].capitalize()
        print(f"  {code}: {state} {calc}")
    print("-" * 40)


def get_validated_input(
    prompt: str, input_type: type = str, validation_func: Optional[callable] = None
) -> Any:
    """
    Prompts the user for input, validates it, and converts to the desired type.

    Args:
        prompt: The message to display to the user.
        input_type: The desired type of the output (e.g., str, int, float).
        validation_func: An optional function to perform custom validation.
                         Should accept the raw input and return True if valid,
                         False otherwise.

    Returns:
        The validated user input, converted to input_type.

    Raises:
        ValueError: If input cannot be converted to the specified type.
        SystemExit: If validation fails repeatedly or input type is invalid.
    """
    while True:
        try:
            user_input_str = input(prompt).strip()
            # Perform type conversion first
            converted_input = input_type(user_input_str)

            # Perform custom validation if provided
            if validation_func:
                if validation_func(converted_input):
                    return converted_input
                else:
                    print("Invalid input. Please try again.")
            else:
                # No custom validation needed, return converted input
                return converted_input

        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")
        except EOFError:
            print("\nInput stream closed. Exiting.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Exiting.")
            sys.exit(1)


def get_calculation_parameters() -> Dict[str, Any]:
    """
    Collects all necessary calculation parameters from the user.

    Returns:
        A dictionary containing the user-specified parameters.
    """
    params: Dict[str, Any] = {}

    params["mol_name"] = get_validated_input("Enter the name of the Molecule: ", str)
    print(
        f"Note: Ensure '{params['mol_name']}.xyz' exists or provide the full path later."
    )

    params["calc_type"] = get_validated_input(
        f"Enter calculation type code ({', '.join(map(str, CALC_TYPE_MAP.keys()))}): ",
        int,
        lambda x: x in CALC_TYPE_MAP,
    )

    params["functional"] = get_validated_input(
        "Enter the name of the functional (e.g., b3lyp): ", str
    )
    params["basis_set"] = get_validated_input(
        "Enter the basis-set (e.g., 6-31g*): ", str
    )
    params["charge"] = get_validated_input("Enter the charge: ", int)
    params["multiplicity"] = get_validated_input("Enter the multiplicity: ", int)

    # Determine if solvent effects should be included
    cosmo_input = get_validated_input(
        "Include Solvent Effects (COSMO)? (y/n): ",
        str,
        lambda x: x.lower() in ["y", "n"],
    )
    params["use_solvent"] = cosmo_input.lower() == "y"
    params["solvent_name"] = None
    params["epsilon"] = None

    if params["use_solvent"]:
        while params["epsilon"] is None:
            solvent_name_input = get_validated_input(
                "Enter the name of the solvent: ", str
            )
            params["solvent_name"] = solvent_name_input.lower()
            params["epsilon"] = SOLVENT_DIELECTRICS.get(params["solvent_name"])
            if params["epsilon"] is None:
                print(
                    f"Error: Solvent '{solvent_name_input}' not found in the list. Please try again."
                )
                # Optional: List available solvents here if needed
                # print("Available solvents:", ", ".join(SOLVENT_DIELECTRICS.keys()))

    # Set default excited state parameters (can be overridden later if needed)
    params["is_excited_state"] = params["calc_type"] in EXCITED_STATE_CALCS
    params["cis_target"] = DEFAULT_CISTARGET
    params["cis_numstates"] = DEFAULT_CIS_NUMSTATES
    params["cis_guessvecs"] = DEFAULT_CIS_NUMSTATES * DEFAULT_CISTARGET

    # Set run type based on calc_type
    params["run_type"] = CALC_TYPE_MAP[params["calc_type"]][1]

    return params


def generate_terachem_input(params: Dict[str, Any]) -> str:
    """
    Generates the TeraChem input file content as a string based on parameters.

    Args:
        params: A dictionary containing the calculation parameters.

    Returns:
        A string containing the formatted TeraChem input file content.
    """
    mol_name = params["mol_name"]
    calc_name, _ = CALC_TYPE_MAP[params["calc_type"]]
    solvent_desc = (
        f"in {params['solvent_name']} (COSMO)"
        if params["use_solvent"]
        else "in gas phase"
    )
    state_desc = "Excited state" if params["is_excited_state"] else "Ground state"
    job_desc = (
        f"{mol_name} {state_desc} {calc_name.split('_')[1]} calculation {solvent_desc}"
    )

    # --- Template Sections ---
    header_tmpl = f"""\
# Job info: {job_desc}
# Generated by Chef-TeraChem (Refactored v{__version__})
#
"""

    coordinates_tmpl = f"""\
# Coordinate file (ensure '{mol_name}.xyz' is accessible)
coordinates        {mol_name.lower()}.xyz
"""

    charge_mult_tmpl = f"""\
# Charge & Multiplicity
charge             {params['charge']}
spinmult           {params['multiplicity']}
"""

    method_basis_run_tmpl = f"""\
# Basis Set, Method (Functional), and Run Type
basis              {params['basis_set']}
method             {params['functional'].lower()}
run                {params['run_type']}
"""

    # Specific options for optimization runs
    minimizer_tmpl = (
        """\
# Optimization specific options
new_minimizer      yes
"""
        if params["run_type"] == "minimize"
        else ""
    )

    # Specific options for frequency runs
    frequency_tmpl = (
        """\
# Frequency specific options
mincheck           false
"""
        if params["run_type"] == "frequencies"
        else ""
    )

    solvent_tmpl = (
        f"""\
# Solvent model (COSMO) and dielectric constant
pcm                cosmo
epsilon            {params['epsilon']:.4f}
"""
        if params["use_solvent"]
        else ""
    )

    excited_state_tmpl = (
        f"""\
# Excited state options (TD-DFT/CIS)
cis                yes
cistarget          {params['cis_target']}
cisnumstates       {params['cis_numstates']}
cisguessvecs       {params['cis_guessvecs']}
"""
        if params["is_excited_state"]
        else ""
    )

    hardware_tmpl = f"""\
# Hardware Information (Adjust as needed)
gpus               {DEFAULT_GPUS}
safemode           no
"""

    expert_opts_tmpl = """\
# Expert options (Uncomment and modify with caution, refer to TeraChem manual)
#precision         double
#threall           1.0e-15
#convthre          3.0e-07
#dftgrid           5
"""

    pcm_expert_opts_tmpl = (
        """\
# PCM Expert options (Uncomment and modify with caution)
#pcm_scale         1
#pcm_grid          lebedev
#pcmgrid_h         7
#pcmgrid_heavy     7
"""
        if params["use_solvent"]
        else ""
    )

    footer_tmpl = "end\n"

    # --- Assemble the input file content ---
    content = (
        header_tmpl
        + coordinates_tmpl
        + charge_mult_tmpl
        + method_basis_run_tmpl
        + minimizer_tmpl
        + frequency_tmpl
        + solvent_tmpl
        + excited_state_tmpl
        + hardware_tmpl
        + expert_opts_tmpl
        + pcm_expert_opts_tmpl  # Add PCM expert options if solvent is used
        + footer_tmpl
    )

    return content


def write_input_file(filename: str, content: str) -> None:
    """
    Writes the generated content to the specified file.

    Args:
        filename: The name of the file to write.
        content: The string content to write to the file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nSuccessfully generated TeraChem input file: '{filename}'")
    except IOError as e:
        print(f"\nError: Could not write file '{filename}'. Reason: {e}")
        sys.exit(1)


def generate_filename(params: Dict[str, Any]) -> str:
    """
    Generates a descriptive filename for the input file.

    Args:
        params: Dictionary of calculation parameters.

    Returns:
        A string representing the suggested filename.
    """
    base_name = params["mol_name"]
    calc_suffix, _ = CALC_TYPE_MAP[params["calc_type"]]
    solvent_suffix = "_cosmo" if params["use_solvent"] else ""
    return f"{base_name}_{calc_suffix}{solvent_suffix}.in"


# --- Main Execution ---


def main() -> None:
    """Main function to run the script."""
    print_header()
    try:
        parameters = get_calculation_parameters()
        input_content = generate_terachem_input(parameters)
        output_filename = generate_filename(parameters)
        write_input_file(output_filename, input_content)
        print("\nTask Completed Successfully.")
        print("Consider buying the original developer a beer!")  # Keeping the spirit :)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure Python 3.6+ for f-strings and type hints
    if sys.version_info < (3, 6):
        print("Error: This script requires Python 3.6 or later.")
        sys.exit(1)
    main()
