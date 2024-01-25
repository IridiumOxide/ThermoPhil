import subprocess
import re
import json


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


class Result:
    velocity: float  # m/s
    pressure: float  # atm
    temperature: float  # K
    enthalpy: float  # cal/g

    def to_dict(self):
        return {
            "velocity": self.velocity,
            "pressure": self.pressure,
            "temperature": self.temperature,
            "enthalpy": self.enthalpy
        }


def result_encoder(obj):
    if isinstance(obj, Result):
        return obj.to_dict()
    return obj


def craft_input_file(base_mixture: Mixture, var_mixture: Mixture, concentration, density=None):
    input_location = "C:\\INPUT"
    total_moles = 10
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
        density_string = f"c-j,p,1.,v,{density}"

# set,bkw,alpha,0.50
# set,bkw,beta,0.403
# set,bkw,kappa,10.86
# set,bkw,theta,5441

    input_template = f"""geos, ideal

for,n2,0.,24465.,0.,n,2
for,o2,0.,24465.,0.,o,2
for,ch4,-17830.,24465.,0.,c,1,h,4

reactants reaction

{com_string}

{density_string}

stop"""

    try:
        with open(input_location, 'w') as file:
            file.write(input_template)
        print(f"Content in '{input_location}' has been replaced.")
    except FileNotFoundError:
        print(f"File not found: {input_location}")
    except Exception as e:
        print(f"An error occurred: {e}")


def find_density():
    output_location = "C:\\output"

    if has_error(output_location):
        return -1

    pattern = re.compile(r'the standard volume is\s+(-?\d+\.\d+)')
    try:
        with open(output_location, 'r') as file:
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
        print(f"File not found: {output_location}")
        return -1
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1


def run_tiger():
    tiger_location = "C:\\TIGER"
    tiger_executable = "TIGER.EXE"
    runnr_location = "C:\\otvdm.exe"
    p = subprocess.Popen([runnr_location, tiger_executable], cwd=tiger_location)
    # p wait causes some weird errors to appear, should look at that
    p.wait()


def analyze_output_file(key, out_dict):
    output_location = "C:\\output"

    if has_error(output_location):
        return

    shock_velo_pattern = re.compile(r'the shock velocity is\s+(-?\d+\.\d+E[+-]\d+)')
    linevals_pattern = re.compile(r'1\.\)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)\s+(\S+)\s+(\S+)')

    result = Result()

    with open(output_location, 'r') as file:
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
    outputs = {}

    # craft_input_file(air, ch4, 0.11)
    # run_tiger()
    # dens = find_density()
    # craft_input_file(air, ch4, 0.11, dens)
    # run_tiger()
    # analyze_output_file(0.11, outputs)

    for conc in [round(i * 0.01, 2) for i in range(1, 100)]:
        print("-------------------")
        print(f"CONC: {conc}")
        craft_input_file(air, ch4, conc)
        run_tiger()
        dens = find_density()
        craft_input_file(air, ch4, conc, dens)
        run_tiger()
        analyze_output_file(conc, outputs)
        print(f"DONE FOR {conc}")

    print(outputs)
    with open("C:\\results.json", "w") as outfile:
        json.dump(outputs, outfile, default=result_encoder, indent=2)
