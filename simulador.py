import random
import os
import csv
from statistics import stdev, mean

## Global Variables
# Write data to a CSV file
FILENAME = "simulation.csv"


COMPONENT_TYPES = ["ADAS", "Powertrain", "HMI", "Body", "Chassis"]
"""The Type of components that can be used in the simulation"""

SAFETY_LEVELS = ["QM", "A", "B", "C", "D"]
""" Define the CAL levels that correspond to each safety level """

CAL_MAPPING = {
    SAFETY_LEVELS[0]: [1, 2],  # CAL levels 1, 2 for QM
    SAFETY_LEVELS[1]: [1, 2, 3],  # CAL levels 1, 2, 3 for A
    SAFETY_LEVELS[2]: [1, 2, 3],  # CAL levels 1, 2, 3 for B
    SAFETY_LEVELS[3]: [2, 3, 4],  # CAL levels 2, 3, 4 for
    SAFETY_LEVELS[4]: [2, 3, 4],  # CAL levels 2, 3, 4 for D
}
""" Define a mapping for interaction risk based on the selected component
High risk     : Impacts autonomous driving decisions; User overrides safety features (e.g., disables lane assist); Affects braking & steering control.
Moderate risk : Sensors impact collision detection; Driver control over powertrain settings; Could alter stability settings.
Low risk      : Structural changes affecting safety.
"""

INTERACTION_RISK_MAP = {
    COMPONENT_TYPES[0]: [
        "High",
        "High",
        "Moderate",
        "Low",
    ],  # ADAS is more likely to have high interaction risk
    COMPONENT_TYPES[1]: [
        "High",
        "Moderate",
        "Low",
        "None",
    ],  # Powertrain has high/moderate risk
    COMPONENT_TYPES[2]: [
        "Moderate",
        "Low",
        "None",
        "None",
    ],  # HMI might have moderate to low risks
    COMPONENT_TYPES[3]: ["Low", "Low", "None", "None"],  # Body has lower risk
    COMPONENT_TYPES[4]: [
        "Moderate",
        "Low",
        "None",
        "None",
    ],  # Chassis tends to have moderate or low risks
}


def generate_simulation_data(
    numberECUs,
    vulnProb,
    categoriesValues,
    maxVuln,
    minVuln,
    adasWeight,
    powertWeight,
    hmiWeight,
    bodyWeight,
    chWeight,
    qmWeight,
    aWeight,
    bWeight,
    cWeight,
    dWeight,
):
    """Generates a list of rows with random data matching the simulation."""
    
    values = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    finalData = []
    vulnsWML = []

    for _ in range(numberECUs):
        # Define component types with specific probabilities
        component_probs = [adasWeight, powertWeight, hmiWeight, bodyWeight, chWeight]
        selected_component = random.choices(COMPONENT_TYPES, weights=component_probs, k=1)[0]

        # Define the safety levels that depend on the CAL levels
        safety_probs = [qmWeight, aWeight, bWeight, cWeight, dWeight]
        selected_asil = random.choices(SAFETY_LEVELS, weights=safety_probs, k=1)[0]
        # Define the CAL levels that correspond to each safety level
        selected_cal = random.choice(CAL_MAPPING[selected_asil])

        # Randomly choose the interaction risk from the INTERACTION_RISK_MAP for the selected component
        interaction_risk = random.choice(INTERACTION_RISK_MAP[selected_component])

        # Probability of generating (0,0,0)
        if random.random() < vulnProb:
            vulnsWML = [0, 0, 0]
        else:
            # Decide how many vulnerabilities to generate (1, 2, or 3)
            num_vulns = random.randint(1, 3)
            # Random W, M, (0 to 6.9)
            vulnsWML = [round(random.uniform(minVuln, maxVuln), 1) for _ in range(num_vulns)]
            # In case we do not have vulns just fill 0
            while len(vulnsWML) < 3:
                {vulnsWML.append(0)}

            # Check if any value in the list is >= 5.3
            if max(vulnsWML) >= 5.3:
                vulnsWML = [max(vulnsWML), 0, 0]
            else:
                vulnsWML.sort(reverse=True)

        data = [
            # Random Types of components
            selected_component,
            # Random ASIL Level
            selected_asil,
            # Random CAL Level (1 to 4)
            selected_cal,
            # Random Data Or Privacy (Yes/No)
            random.choice(["Yes", "No"]),
            # Random Isolated Entity (Yes/No)
            random.choice(["Yes", "No"]),
            interaction_risk,
            vulnsWML[0],
            vulnsWML[1],
            vulnsWML[2],
        ]
        # Component rating based (-0.725 * result) + 5 with one decimal
        data.append(round(componentRatingCalculus(vulnsWML[0], vulnsWML[1], vulnsWML[2]), 1))
        # Vehicle Rating
        # 1 = ASIL Level,
        # 2 = CAL Level,
        # 3 = Data Or Privacy,
        # 4 = Isolated Entity,
        # 5 = interaction risk associated to each component
        # 9 = Component rating
        data.append(vehicleRatingCalculus(values, categoriesValues, data[1], data[2], data[3], data[4], data[5], data[9]))
        finalData.append(data)

def checkVulnRange(val: float) -> float:
    """Validate and adjust input values to be within [0.1, 6.9]"""

    if val < 0.0:
        return 0
    elif val > 6.9:
        return 6.9
    else:
        return val


def componentRatingCalculus(valW: float, valM: float, valL: float) -> float:
    """Calculates the component 5-grade rating based on the input values."""

    # Validate and adjust input values to be within [0.1, 6.9]
    valW = checkVulnRange(valW)
    valM = checkVulnRange(valM)
    valL = checkVulnRange(valL)

    # Count valid inputs
    valid_values = [val for val in [valW, valM, valL] if val > 0]
    count_available = len(valid_values)

    # Compute the weighted result based on the number of valid inputs
    if count_available == 3:  # All three values are available
        result = (valW * 0.6) + (valM * 0.3) + (valL * 0.1)
    elif count_available == 2:  # Only two values are available
        # Sort valid values in descending order
        valid_values.sort(reverse=True)
        # Use the two highest values with weights 0.6 and 0.4
        result = (valid_values[0] * 0.6) + (valid_values[1] * 0.4)
    elif count_available == 1:  # Only one value is available
        # Use the single available value
        result = valid_values[0]
    else:  # No values are available
        result = 0

    # Apply the adaptation formula to compute the final grade
    componentRatingfinal_grade = (-0.725 * result) + 5

    return componentRatingfinal_grade

def addComponentToCategory(categoriesValues, asil, cal, dp, iso, risk, cRating):
    """Adds the current component to the correct category"""

    # Check if component rating is between 0 and 5
    if cRating >= 0 and cRating <= 5:
        # Class D
        if (asil == "D" or asil == "C") or ((asil == "B" or asil == "A") and (cal == 4 or cal == 3) and risk == "High"):
            categoriesValues[0].append(cRating)

        # Class C
        elif ((asil == "B" or asil == "A") and cal == 2 and dp == "Yes") or risk in ["Moderate", "Low"]:
            categoriesValues[1].append(cRating)

        # Class B
        elif ((asil == "B" or asil == "A") and cal == 2 and dp == "No" and iso == "No") or risk in ["Low", "None"]:
            categoriesValues[2].append(cRating)

        # Class A (other types)
        else:
            categoriesValues[3].append(cRating)

    return categoriesValues

def vehicleRatingCalculus(values, categoriesValues, asil, cal, dp, iso, risk, cRating):
    """Calculates the vehicle 5-grade rating part A"""

    # Check if component rating is between 0 and 5
    if cRating >= 0 and cRating <= 5:
        # Class D
        if (asil == "D" or asil == "C") or ((asil == "B" or asil == "A") and (cal == 4 or cal == 3) and risk == "High"):
            values[0][0] += round(cRating, 2)
            values[0][1] += 1
            categoriesValues[0].append(cRating)

        # Class C
        elif ((asil == "B" or asil == "A") and cal == 2 and dp == "Yes") or risk in ["Moderate", "Low"]:
            values[1][0] += round(cRating, 2)
            values[1][1] += 1
            categoriesValues[1].append(cRating)

        # Class B
        elif ((asil == "B" or asil == "A") and cal == 2 and dp == "No" and iso == "No") or risk in ["Low", "None"]:
            values[2][0] += round(cRating, 2)
            values[2][1] += 1
            categoriesValues[2].append(cRating)

        # Class A (other types)
        else:
            values[3][0] += round(cRating, 2)
            values[3][1] += 1
            categoriesValues[3].append(cRating)

    values[0][-1] = values[1][-1] = values[2][-1] = values[3][-1] = round(vehicleRatingWeightCalculus(values), 2)

    return values

def vehicleRatingWeightCalculus(categoriesValues):
    """ Calculates the vehicle 5-grade rating part B """

    weights = [0.5, 0.3, 0.15, 0.05]
    finalScore = 0
    adjusted_weights = []
    total_weight = 0

    # Adjust weights and calculate the total weight for non-missing values
    for i in range(len(values)):
        # Check if the counter of detected values is greater than 0
        if values[i][1] > 0:
            adjusted_weights.append(weights[i])
            total_weight += weights[i]

    for i in range(len(values)):
        if values[i][1] > 0:
            # Normalize the weights
            averageRating = values[i][0] / values[i][1]
            normalized_weight = weights[i] / total_weight
            finalScore += normalized_weight * averageRating

    print(values)
    print(round(finalScore, 2))

    return finalScore



def write_to_file(data, categoriesValues):
    """Write the generated simulation data to a CSV file."""

    file_exists = os.path.exists(FILENAME)

    with open(FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")

        if not file_exists:
            # Define header for the CSV file
            header = [
                # "Component Type", "ASIL Level", "CAL Level", "Data/Privacy",
                # "Isolated Entity", "Interation Risk", "W", "M", "L", "Component Rating",
                "sum_D",
                "n_Times_D",
                "Avg_D",
                "mean_D",
                "std_D",
                "sum_C",
                "n_Times_C",
                "Avg_C",
                "mean_C",
                "std_C",
                "sum_B",
                "n_Times_B",
                "Avg_B",
                "mean_B",
                "std_B",
                "sum_A",
                "n_Times_A",
                "Avg_A",
                "mean_A",
                "std_A",
                "Final Rating",
            ]
            writer.writerow(header)  # Write the header row

        # Write simulation label as a separator row
        for row in data:
            # Get the final rating of the simulation
            for i in range(3):  # row[10][3] has 4 elements
                if row[10][i][2] != 0:
                    final_rating = row[10][i][2]
                    break
                else:
                    final_rating = 0

        # D data (avg, mean and stdev)
        avg_D = sum(categoriesValues[0]) / len(categoriesValues[0]) if len(categoriesValues[0]) > 0 else 0
        stdev_D = stdev(categoriesValues[0]) if len(categoriesValues[0]) > 1 else 0
        mean_D = mean(categoriesValues[0]) if len(categoriesValues[0]) > 0 else 0
        # C data (avg, mean and stdev)
        avg_C = sum(categoriesValues[1]) / len(categoriesValues[1]) if len(categoriesValues[1]) > 0 else 0
        stdev_C = stdev(categoriesValues[1]) if len(categoriesValues[1]) > 1 else 0
        mean_C = mean(categoriesValues[1]) if len(categoriesValues[1]) > 0 else 0
        # B data (avg, mean and stdev)
        avg_B = sum(categoriesValues[2]) / len(categoriesValues[2]) if len(categoriesValues[2]) > 0 else 0
        stdev_B = stdev(categoriesValues[2]) if len(categoriesValues[2]) > 1 else 0
        mean_B = mean(categoriesValues[2]) if len(categoriesValues[2]) > 0 else 0
        # A data (avg, mean and stdev)
        avg_A = sum(categoriesValues[3]) / len(categoriesValues[3]) if len(categoriesValues[3]) > 0 else 0
        stdev_A = stdev(categoriesValues[3]) if len(categoriesValues[3]) > 1 else 0
        mean_A = mean(categoriesValues[3]) if len(categoriesValues[3]) > 0 else 0

        writer.writerow(
            [
                # row[0],   # Component Type
                # row[1],   # ASIL Level
                # row[2],   # CAL Level
                # row[3],   # Data/Privacy
                # row[4],   # Isolated Entity
                # row[5],   # interation Risk
                # row[6],   # W
                # row[7],   # M
                # row[8],   # L
                # row[9],   # Component Rating
                row[10][0][0],  # sum D
                row[10][0][1],  # n Times D
                avg_D,  # Avg D
                mean_D,  # mean D
                stdev_D,  # stdev D
                row[10][1][0],  # sum C
                row[10][1][1],  # n Times C
                avg_C,  # Avg C
                mean_C,  # mean C
                stdev_C,  # stdev C
                row[10][2][0],  # sum B
                row[10][2][1],  # n Times B
                avg_B,  # Avg B
                mean_B,  # mean B
                stdev_B,  # stdev B
                row[10][3][0],  # sum A
                row[10][3][1],  # n Times A
                avg_A,  # Avg A
                mean_A,  # mean A
                stdev_A,  # stdev A
                final_rating,
            ]
        )
        # writer.writerows(data)  # Write the data rows
        print(f"Data written to {FILENAME}")


def main():
    # Generate data for n components
    type = input("Choose the simulation type (auto or manual): ").strip()

    if type == "auto":
        n = int(input("How many times would you like to repeat the simulation: "))
        numberECUs = 50  # random.randint(1, 30)
        for _ in range(n):
            categoriesValues = [[], [], [], []]
            vulnProb = round(random.uniform(0, 1), 1)
            minVuln = 0  # Min value allowed
            maxVuln = 6.9  # Max value allowed is 6.9
            seedValue = random.randint(1, 10000)
            # ADAS, Powertrain, HMI, Body, Chassis
            domainWeight = [0.20, 0.20, 0.20, 0.20, 0.20]
            # QM, A, B, C, D
            safetyWeight = [0.20, 0.20, 0.20, 0.20, 0.20]
            data = generate_simulation_data(
                numberECUs,
                vulnProb,
                categoriesValues,
                maxVuln,
                minVuln,
                domainWeight[0],
                domainWeight[1],
                domainWeight[2],
                domainWeight[3],
                domainWeight[4],
                safetyWeight[0],
                safetyWeight[1],
                safetyWeight[2],
                safetyWeight[3],
                safetyWeight[4],
            )
            write_to_file(data, categoriesValues)
    elif type == "manual":
        numberECUs = int(input("How many ECU's do you wish to simulate (e.g values between 0 and 100): "))
        vulnProb = float(input("Enter the probability of generating components without vulnerabilities (e.g values between 0 and 1): "))
        maxVuln = float(input("Enter the probability of generating components without vulnerabilities (e.g values between 0 and 6.9): "))
        seedValue = int(input("Enter your seed for the random generator (e.g values between 0 and 1000): "))
        domainWeight = [
            # Type ADAS
            float(input("Enter probability for generating components type ADAS (e.g values between 0 and 1):")),
            # Type PowerTrain
            float(input("Enter probability for generating components type ADAS (e.g values between 0 and 1):")),
            # Type HMI
            float(input("Enter probability for generating components type ADAS (e.g values between 0 and 1):")),
            # Type Body
            float(input("Enter probability for generating components type ADAS (e.g values between 0 and 1):")),
            # Type Chassi
            float(input("Enter probability for generating components type ADAS (e.g values between 0 and 1):")),
        ]
        safetyWeight = [
            # Type QM
            float(input("Enter probability for generating components with safety level of QM (e.g values between 0 and 1):")),
            # Type A
            float(input("Enter probability for generating components with safety level of A (e.g values between 0 and 1):")),
            # Type B
            float(input("Enter probability for generating components with safety level of B (e.g values between 0 and 1):")),
            # Type C
            float(input("Enter probability for generating components with safety level of C (e.g values between 0 and 1):")),
            # Type D
            float(input("Enter probability for generating components with safety level of D (e.g values between 0 and 1):")),
        ]
        data = generate_simulation_data(
            numberECUs,
            vulnProb,
            categoriesValues,
            maxVuln,
            minVuln,
            domainWeight[0],
            domainWeight[1],
            domainWeight[2],
            domainWeight[3],
            domainWeight[4],
            safetyWeight[0],
            safetyWeight[1],
            safetyWeight[2],
            safetyWeight[3],
            safetyWeight[4],
        )
        write_to_file(data)
    else:
        print("Wrong Data")


if __name__ == "__main__":
    # Declaration and track of all of the vehicle 5-grade rating values
    main()
