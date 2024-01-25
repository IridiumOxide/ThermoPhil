import json
import matplotlib.pyplot as plt


def plot_from_json(json_filepath):
    with open(json_filepath, 'r') as json_file:
        data = json.load(json_file)

    x_values = [float(key) for key in data.keys()]
    velocities = [entry["velocity"] for entry in data.values()]
    pressures = [entry["pressure"] for entry in data.values()]
    temperatures = [entry["temperature"] for entry in data.values()]
    enthalpies = [entry["enthalpy"] for entry in data.values()]

    # Plotting
    plt.figure(figsize=(12, 8))

    # Plot 1: Velocity
    plt.subplot(2, 2, 1)
    plt.plot(x_values, velocities, marker='o', linestyle='-')
    max_velocity_index = velocities.index(max(velocities))
    plt.annotate(f'({x_values[max_velocity_index]:.2f}, {velocities[max_velocity_index]:.2f})',
                 xy=(x_values[max_velocity_index], velocities[max_velocity_index]),
                 xytext=(x_values[max_velocity_index] + 0.01, velocities[max_velocity_index] + 10),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))
    plt.title('Velocity')
    plt.xlabel('Methane molar fraction')
    plt.ylabel('Velocity (m/s)')

    # Plot 2: Pressure
    plt.subplot(2, 2, 2)
    plt.plot(x_values, pressures, marker='o', linestyle='-')
    max_pressure_index = pressures.index(max(pressures))
    plt.annotate(f'({x_values[max_pressure_index]:.2f}, {pressures[max_pressure_index]:.2f})',
                 xy=(x_values[max_pressure_index], pressures[max_pressure_index]),
                 xytext=(x_values[max_pressure_index] + 0.01, pressures[max_pressure_index] + 1),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))
    plt.title('Pressure')
    plt.xlabel('Methane molar fraction')
    plt.ylabel('Pressure (atm)')

    # Plot 3: Temperature
    plt.subplot(2, 2, 3)
    plt.plot(x_values, temperatures, marker='o', linestyle='-')
    max_temperature_index = temperatures.index(max(temperatures))
    plt.annotate(f'({x_values[max_temperature_index]:.2f}, {temperatures[max_temperature_index]:.2f})',
                 xy=(x_values[max_temperature_index], temperatures[max_temperature_index]),
                 xytext=(x_values[max_temperature_index] + 0.01, temperatures[max_temperature_index] + 10),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))
    plt.title('Temperature')
    plt.xlabel('Methane molar fraction')
    plt.ylabel('Temperature (K)')

    # Plot 4: Enthalpy
    plt.subplot(2, 2, 4)
    plt.plot(x_values, enthalpies, marker='o', linestyle='-')
    max_enthalpy_index = enthalpies.index(max(enthalpies))
    plt.annotate(f'({x_values[max_enthalpy_index]:.2f}, {enthalpies[max_enthalpy_index]:.2f})',
                 xy=(x_values[max_enthalpy_index], enthalpies[max_enthalpy_index]),
                 xytext=(x_values[max_enthalpy_index] + 0.01, enthalpies[max_enthalpy_index] + 5),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))
    plt.title('Enthalpy')
    plt.xlabel('Methane molar fraction')
    plt.ylabel('Enthalpy (cal/g)')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    json_file_path = "C:\\results.json"
    plot_from_json(json_file_path)
