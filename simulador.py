import argparse
import random
import os
import csv
from statistics import stdev, median

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
   
    finalData = []
    vulnsWML = []

    component_probs = [adasWeight, powertWeight, hmiWeight, bodyWeight, chWeight]
    # Choose numberECUs components randomly with the given probabilities and replacement
    list_selected_components = random.choices(COMPONENT_TYPES, weights=component_probs, k=numberECUs)
    safety_probs = [qmWeight, aWeight, bWeight, cWeight, dWeight]

    for selected_component in list_selected_components:
        # Define the safety levels that depend on the CAL levels
        selected_asil = random.choices(SAFETY_LEVELS, weights=safety_probs, k=1)[0]

        # within the existing CAL choose a level randomly with equal probability
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
                vulnsWML.append(0)

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
            vulnsWML[2]
        ]
        # Component rating based (-0.725 * result) + 5 with one decimal
        data.append(round(componentRatingCalculus(vulnsWML[0], vulnsWML[1], vulnsWML[2]), 1))
        # Vehicle Rating
        # 1 = ASIL Level,
        # 2 = CAL Level,
        # 3 = Data Or Privacy,
        # 4 = Isolated Entity,
        # 5     = interaction risk associated to each component
        # 9 = Component rating
        #data.append(vehicleRatingCalculus(values, categoriesValues, data[1], data[2], data[3], data[4], data[5], data[9]))
        categoriesValues = addComponentToCategory(categoriesValues, data[1], data[2], data[3], data[4], data[5], data[9])
        finalData.append(data)
    # after doing all the components calculate car rating
    finalRating = vehicleRatingWeightCalculus(categoriesValues)

    return (finalData,categoriesValues, finalRating)


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

def vehicleRatingWeightCalculus(categoriesValues):
    """ Calculates the vehicle 5-grade rating part B """

    weights = [0.5, 0.3, 0.15, 0.05]
    finalScore = 0
    adjusted_weights = []
    total_weight = 0
    values = [[0,0],[0,0],[0,0],[0,0]]
    for category in range(len(categoriesValues)):
        values[category][0] = sum(categoriesValues[category])
        values[category][1] = len(categoriesValues[category])

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



def write_to_file(data, categoriesValues, finalRating=0.0):
    """Write the generated simulation data to a CSV file."""

    file_exists = os.path.exists(FILENAME)

    with open(FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")

        if not file_exists:
            # Define header for the CSV file
            writer.writerow([
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
            ]) # Write the header row

        num = [0,0,0,0]
        avg = [0.0,0.0,0.0,0.0]
        std = [0.0,0.0,0.0,0.0]
        med = [0.0,0.0,0.0,0.0]
        summ = [0.0,0.0,0.0,0.0]
        for i in  range(len(num)):
            num[i] = len(categoriesValues[i])
            if  num[i] > 0:
                summ[i]= sum(categoriesValues[i])
                avg[i] = summ[i] / num[i]
                std[i] = stdev(categoriesValues[i]) if num[i]>1 else 0
                med[i] = median(categoriesValues[i]) 

        writer.writerow(
            [
                summ[0],  # sum D
                num[0],  # n Times D
                avg[0],  # Avg D
                med[0],  # mean D
                std[0],  # stdev D

                summ[1],  # sum C
                num[1],  # n Times C
                avg[1],  # Avg C
                med[1],  # mean C
                std[1],  # stdev C

                summ[2],  # sum B
                num[2],  # n Times B
                avg[2],  # Avg B
                med[2],  # mean B
                std[2],  # stdev B

                summ[3],  # sum A
                num[3],  # n Times A
                avg[3],  # Avg A
                med[3],  # mean A
                std[3],  # stdev A
                finalRating
            ]
        )
        
        print(f"Data written to {FILENAME}")

# TODO: get values from file to runit more times
def main():
    # Use argparse as described in
    # https://docs.python.org/3/howto/argparse.html#argparse-tutorial
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--type",help="the simulation type (auto or manual)", choices=["auto", "manual"])
    parser.add_argument("-n","--runs",help="the number of times to run the simulation; greater than 0", type=int)
    parser.add_argument("-s","--seed",help="the seed value to be set (0 to randomize seed)", type=int)
    args = parser.parse_args()

    type = args.type
    if not type:
        type = input("Choose the simulation type (auto or manual): ").strip()
    seedValue = args.seed
    if seedValue is None: # can be 0, which is false
        seedValue = float(input("Enter seed value to be set (0 to randomize seed):"))

    if seedValue == 0:
        seedValue = random.randint(1, 10000)
    print(f"Using seed {seedValue}")
    random.seed(seedValue)
    # TODO: save seed value in some structure

    # default values, can be set on manual
    minVuln = 0  # Min value allowed
    maxVuln = 6.9  # Max value allowed is 6.9
    categoriesValues = [[], [], [], []]
    nr_runs = 1
    # ADAS, Powertrain, HMI, Body, Chassis
    domainWeight = [0.20, 0.20, 0.20, 0.20, 0.20]
    # QM, A, B, C, D
    safetyWeight = [0.20, 0.20, 0.20, 0.20, 0.20]
    numberECUs = 50
    vulnProb = 0

    if type == "auto":
        nr_runs = args.runs
        if not nr_runs: # cannot be zero
            nr_runs = int(input("How many times would you like to repeat the simulation: "))
    
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
    else:
        print("Wrong Data")
    for _ in range(nr_runs):
        categoriesValues = [[], [], [], []] # reset in every run
        if type == "auto": # randomize for each run
            vulnProb = round(random.uniform(0, 1), 1)
    
        (finalData,categoriesValues,finalRating) = generate_simulation_data(
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
        write_to_file(finalData, categoriesValues, finalRating)

if __name__ == "__main__":
    # Declaration and track of all of the vehicle 5-grade rating values
    main()
