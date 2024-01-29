import csv
import datetime
import json
import re
import subprocess
from typing import Callable

# FILESYSTEM CONSTANTS

result_format = "csv"

tiger_dir = "C:\\TIGER"
tiger_executable_name = "TIGER.EXE"
runnr_filepath = "C:\\otvdm.exe"
input_filepath = tiger_dir + "\\INPUT"
output_filepath = tiger_dir + "\\output"
results_dir = "C:\\"


def run_tiger():
    p = subprocess.Popen([runnr_filepath, tiger_executable_name], cwd=tiger_dir)
    # p wait causes some weird errors to appear, probably because TIGER return wrong exit codes
    p.wait()

# END OF CONSTANTS

# MIXTURE DEFINITIONS


class Mixture:
    parts = {}

    def __init__(self, parts):
        self.parts = parts


air = Mixture({
    "o2": 0.21,
    "n2": 0.79,
})
ch4 = Mixture({
    "ch4": 1,
})
c2h2 = Mixture({
    "c2h2": 1,
})
c2h6 = Mixture({
    "c2h6": 1,
})

# END OF MIXTURE DEFINITIONS

# INPUT TEMPLATES (TODO: get formulas from some shared data)


def ch4_input(com_string, density_string):
    return f"""geos, ideal

for,n2,0.,24465.,0.,n,2
for,o2,0.,24465.,0.,o,2
for,ch4,-17830.,24465.,0.,c,1,h,4

reactants reaction

{com_string}

{density_string}

stop"""


def c2h2_input(com_string, density_string):
    return f"""geos, ideal

set,bkw,alpha,0.50
set,bkw,beta,0.403
set,bkw,kappa,10.86
set,bkw,theta,5441


for,n2,0.,24465.,0.,n,2
for,o2,0.,24465.,0.,o,2
for,c2h2,54350.,24465.,0.,c,2,h,2

reactants reaction

{com_string}

{density_string}

stop"""


def c2h6_input(com_string, density_string):
    return f"""geos, ideal
for,n2,0.,24465.,0.,n,2
for,o2,0.,24465.,0.,o,2
for,c2h6,20076.,24465.,0.,c,2,h,6
{com_string}
{density_string}
stop"""

# END OF INPUT TEMPLATES


# TODO: reaction products could be configurable...
class Result:
    velocity: float             # m/s
    pressure: float             # atm
    temperature: float          # K
    enthalpy: float             # cal/g

    product_c: float            # mol/kg
    product_c2n: float          # mol/kg
    product_ch4: float          # mol/kg
    product_co: float           # mol/kg
    product_co2: float          # mol/kg
    product_h2: float           # mol/kg
    product_h2o: float          # mol/kg
    product_hcn: float          # mol/kg
    product_hco: float          # mol/kg
    product_n2: float           # mol/kg
    product_nh3: float          # mol/kg
    product_no: float           # mol/kg
    product_no2: float          # mol/kg
    product_n2o: float          # mol/kg
    product_o2: float           # mol/kg
    product_total_gas: float    # mol/kg

    def to_dict(self):
        return {
            "velocity": self.velocity,
            "pressure": self.pressure,
            "temperature": self.temperature,
            "enthalpy": self.enthalpy,
            "product_c": self.product_c,
            "product_c2n": self.product_c2n,
            "product_ch4": self.product_ch4,
            "product_co": self.product_co,
            "product_co2": self.product_co2,
            "product_h2": self.product_h2,
            "product_h2o": self.product_h2o,
            "product_hcn": self.product_hcn,
            "product_hco": self.product_hco,
            "product_n2": self.product_n2,
            "product_nh3": self.product_nh3,
            "product_no": self.product_no,
            "product_no2": self.product_no2,
            "product_n2o": self.product_n2o,
            "product_o2": self.product_o2,
            "product_total_gas": self.product_total_gas,
        }

    def to_list(self):
        return [
            self.velocity,
            self.pressure,
            self.temperature,
            self.enthalpy,
            self.product_c,
            self.product_c2n,
            self.product_ch4,
            self.product_co,
            self.product_co2,
            self.product_h2,
            self.product_h2o,
            self.product_hcn,
            self.product_hco,
            self.product_n2,
            self.product_nh3,
            self.product_no,
            self.product_no2,
            self.product_n2o,
            self.product_o2,
            self.product_total_gas,
        ]


def result_encoder(obj):
    if isinstance(obj, Result):
        return obj.to_dict()
    return obj


def craft_input_file(
        base_mixture: Mixture,
        var_mixture: Mixture,
        input_template: Callable[[str, str], str],
        concentration: float,
        density=None
):
    total_moles = 10  # should make no difference but might check that later
    var_moles = concentration * total_moles
    base_moles = total_moles - var_moles

    all_parts = {}

    for key, value in base_mixture.parts.items():
        if key in all_parts:
            all_parts[key] += base_moles * value
        else:
            all_parts[key] = base_moles * value

    for key, value in var_mixture.parts.items():
        if key in all_parts:
            all_parts[key] += var_moles * value
        else:
            all_parts[key] = var_moles * value

    com_string = "com,"

    for key, value in all_parts.items():
        com_string += key + ","
        com_string += f"{value:.3f}" + ","

    com_string += "mole"

    density_string = ""

    if density == -1:
        print("Density is wrong, aborting")
        return

    if density is not None:
        density_string = f"c-j,p,1.,v,{density}"  # assuming default c-j

    input_content = input_template(com_string, density_string)

    try:
        with open(input_filepath, 'w') as file:
            file.write(input_content)
        print(f"Content in '{input_filepath}' has been replaced.")
    except FileNotFoundError:
        print(f"File not found: {input_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")


def find_density():
    if has_error(output_filepath):
        return -1

    pattern = re.compile(r'the standard volume is\s+(-?\d+\.\d+)')
    try:
        with open(output_filepath, 'r') as file:
            file_content = file.read()

        match = pattern.search(file_content)

        if match:
            extracted_number = float(match.group(1))
            print(f"The extracted specific volume is: {extracted_number}")
            return extracted_number
        else:
            print("No match found.")
            return -1
    except FileNotFoundError:
        print(f"File not found: {output_filepath}")
        return -1
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1


def analyze_output_file(key, out_dict):
    if has_error(output_filepath):
        return

    shock_velo_pattern = re.compile(r'the shock velocity is\s+(-?\d+\.\d+E[+-]\d+)')
    linevals_pattern = re.compile(r'1\.\)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)\s+(\S+)\s+(\S+)')

    result = Result()

    with open(output_filepath, 'r') as file:
        file_content = file.read()

        shock_velo_match = shock_velo_pattern.search(file_content)
        if shock_velo_match:
            shock_velo = float(shock_velo_match.group(1))
            result.velocity = shock_velo
            print(f"The extracted shock velocity is: {shock_velo}")
        else:
            print("No match found.")

        linevals_match = linevals_pattern.search(file_content)
        if linevals_match:
            pressure = float(linevals_match.group(1))
            temperature = float(linevals_match.group(3))
            enthalpy = float(linevals_match.group(4))

            result.pressure = pressure
            result.temperature = temperature
            result.enthalpy = enthalpy

            print(f"The extracted pressure is: {pressure}")
            print(f"The extracted temperature is: {temperature}")
            print(f"The extracted enthalpy is: {enthalpy}")
        else:
            print("No match found.")

        # gas residues
        prods = ["ch4", "c2n", "co", "co2", "h2", "h2o", "hcn", "hco", "n2", "nh3", "no", "no2", "n2o", "o2"]
        for prod in prods:
            regexp = re.compile(fr'\b{prod}\b\s+gas\s+([\d.]+)')
            match = regexp.search(file_content)
            concentration = 0.0
            if match:
                concentration = match.group(1)
            else:
                print(f'{prod} unmatched!')
            setattr(result, f'product_{prod}', concentration)

        # total gas residue
        regexp = re.compile(fr'\btotal\b\s+gas\s+([\d.]+)')
        match = regexp.search(file_content)
        concentration = 0.0
        if match:
            concentration = match.group(1)
        result.product_total_gas = concentration

        # solid residues
        regexp = re.compile(fr'{re.escape("*c")}\s+soli\s+([\d.]+)')
        match = regexp.search(file_content)
        concentration = 0.0
        if match:
            concentration = match.group(1)
        result.product_c = concentration

    out_dict[key] = result


def has_error(filename):
    error_iteration_exceeded = "iteration exceeded"
    errors = [error_iteration_exceeded]

    error_happened = False

    with open(filename, 'r') as file:
        for line in file:
            for e in errors:
                if e in line:
                    # REMOVE DEBUG PRINT
                    print(e)
                    error_happened = True
                    break

    return error_happened


if __name__ == '__main__':

    results = {}

    # craft_input_file(air, c2h6, c2h6_input, 0.01)
    # run_tiger()
    # dens = find_density()
    # craft_input_file(air, c2h6, c2h6_input, 0.01, dens)
    # run_tiger()
    # analyze_output_file(0.01, results)

    # for conc in [round(i*0.01, 2) for i in range(1, 100)]:
    for conc in [round(i*0.01, 2) for i in range(1, 41)] + [round(i*0.01, 2) for i in range(45, 96, 5)]:
        print("-------------------")
        print(f"CONC: {conc}")
        craft_input_file(air, c2h2, c2h2_input, conc)
        run_tiger()
        dens = find_density()
        craft_input_file(air, c2h2, c2h2_input, conc, dens)
        run_tiger()
        analyze_output_file(conc, results)
        print(f"DONE FOR {conc}")

    print(results)

    results_filename = (results_dir + "\\results_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        + "." + result_format)
    if result_format == "json":
        with open(results_filename, "w") as outfile:
            json.dump(results, outfile, default=result_encoder, indent=2)
    elif result_format == "csv":
        with open(results_filename, 'w', newline='') as csv_file:
            # Create a CSV writer object
            csv_writer = csv.writer(csv_file)

            # Write the header (column names)
            header = ["concentration"] + list(Result().__annotations__.keys())
            csv_writer.writerow(header)

            # Write data for each Result object
            for key, result in results.items():
                csv_writer.writerow([key] + result.to_list())
    else:
        print("UNKNOWN OUTPUT FORMAT!")
