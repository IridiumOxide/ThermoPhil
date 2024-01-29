import json
import matplotlib.pyplot as plt

plots_dir = 'C:\\tiger_plots'
result_file = "C:\\results.json"


def plot_from_json(json_filepath):
    with open(json_filepath, 'r') as json_file:
        data = json.load(json_file)

    x_values = [float(key) for key in data.keys()]

    # Attributes to plot with additional information
    attributes_to_plot = [
        {"name": "velocity", "title": "Velocity", "xlabel": "Methane molar fraction", "ylabel": "Velocity (m/s)"},
        {"name": "pressure", "title": "Pressure", "xlabel": "Methane molar fraction", "ylabel": "Pressure (atm)"},
        {"name": "temperature", "title": "Temperature", "xlabel": "Methane molar fraction", "ylabel": "Temperature (K)"},
        {"name": "enthalpy", "title": "Reaction enthalpy", "xlabel": "Methane molar fraction", "ylabel": "Enthalpy (cal/g)"},
        {"name": "specific_volume", "title": "Specific Volume", "xlabel": "Methane molar fraction", "ylabel": "Specific Volume (cc/g)"},
        {"name": "product_ch4", "title": "CH4 in products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
        {"name": "product_co", "title": "CO in products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
        {"name": "product_co2", "title": "CO2 in products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
        {"name": "product_h2", "title": "H2 in products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
        {"name": "product_h2o", "title": "H2O in products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
        {"name": "product_n2", "title": "N2 in products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
        {"name": "product_o2", "title": "O2 in products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
        {"name": "product_total_gas", "title": "Total gas products", "xlabel": "Methane molar fraction", "ylabel": "Amount of product (mol / kg of explosive)"},
    ]

    # Plotting
    for attribute_info in attributes_to_plot:
        plt.figure(figsize=(10, 6))
        attribute = attribute_info["name"]
        attribute_values = [float(entry[attribute]) for entry in data.values()]
        plt.plot(x_values, attribute_values, marker='o', linestyle='-')
        max_index = attribute_values.index(max(attribute_values))
        plt.annotate(f'({x_values[max_index]:.2f}, {attribute_values[max_index]:.2f})',
                     xy=(x_values[max_index], attribute_values[max_index]),
                     xytext=(x_values[max_index] + 0.01, attribute_values[max_index] + 1),
                     arrowprops=dict(facecolor='black', arrowstyle='->'))
        plt.title(attribute_info["title"])
        plt.xlabel(attribute_info["xlabel"])
        plt.ylabel(attribute_info["ylabel"])
        plt.tight_layout()

        output_path = plots_dir + f'\\{attribute}_plot.png'
        plt.savefig(output_path)
        plt.close()

    # Product fields to plot
    product_fields = [
        "product_ch4",
        "product_co",
        "product_co2",
        "product_h2",
        "product_h2o",
        "product_n2",
        "product_o2",
    ]

    plt.figure(figsize=(12, 8))

    for product_field in product_fields:
        values = [float(entry[product_field]) for entry in data.values()]
        plt.plot(x_values, values, marker='o', linestyle='-', label=product_field)

    plt.title('Gas products')
    plt.xlabel('Methane molar fraction')
    plt.ylabel('Amount of product (mol / kg of explosive)')
    plt.legend()
    plt.tight_layout()

    # Save the combined plot as an image in the output folder
    output_path = plots_dir + f'\\all_products_plot.png'
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    plot_from_json(result_file)
