import argparse
import json
import pickle
import random
import os
import csv
from statistics import stdev, median

## Global Variables
# Write data to a CSV file
FILENAME_RESULTS = "simulation.csv"
FILENAME_RAW = "data.txt"

COMPONENT_TYPES = ["ADAS", "Powertrain", "HMI", "Body", "Chassis"]
"""The Type of components that can be used in the simulation"""

SECURITY_FEATURES = {
"""
SECURITY_FEATURES dictionary with assumed weight values.
- Base vulnerability probability is 1.0 (ECU completely unsecure).
- Minimum achievable vulnerability probability is 0.05 (no system can be fully secure).
- Weights represent how much each feature reduces vulnerability.
- Sub-features are mutually exclusive within their parent feature (e.g., JTAG locks, Firewalls, Secure Diagnostics).
- These weights are illustrative assumptions and should be adapted to real risk based on industry alignments.
"""
    # ----------------------------
    # Intrusion Systems
    # ----------------------------
    "IDS - AI Intrusion Detection": 0.02,
    "IPS - AI Intrusion Prevention": 0.02,

    # ----------------------------
    # Secure Boot & Firmware Updates
    # ----------------------------
    "Secure Boot": 0.06,
    "Secure Flashing": 0.06,
    "Secure Updates (OTA)": 0.05,

    # ----------------------------
    # Secure Communication & Debugging (includes JTAG locks with (mutually exclusive))
    # ----------------------------
    "Secure Communication (SECoc)": 0.05,
    "JTAG Lock": {
        "JTAG Lock - Single Password": 0.015,
        "JTAG Lock - Individual Password Per ECU": 0.025
    },

    # ----------------------------
    # Secure Diagnostics (mutually exclusive)
    # ----------------------------
    "Secure Diagnostics": {
        "Secure Diagnostics (UDS 0x27 - SecurityAccess)": 0.015,
        "Secure Diagnostics (UDS 0x29 - Authenticated)": 0.025
    },

    # ----------------------------
    # Hardware Security Module (HSM)
    # ----------------------------
    "HSM - Secure Key Storage": 0.05,

    # ----------------------------
    # Firewalls
    # ----------------------------
    "Firewall": {
        "Firewall - Whitelist-Based": 0.06,
        "Firewall - Blacklist-Based": 0.04
    },
    "AI Firewall Adaptation": 0.07, 

    # ----------------------------
    # Real-time & Fleet Learning
    # ----------------------------
    "Real-time Attack Adaptation": 0.09,
    "AI Learning & Fleet-wide Update": 0.07,
}


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
        if random.random() > vulnProb:
            vulnsWML = [0, 0, 0]
        # Probability of generating vulns
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
            vulnsWML[2],
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
        # data.append(vehicleRatingCalculus(values, categoriesValues, data[1], data[2], data[3], data[4], data[5], data[9]))
        categoriesValues = addComponentToCategory(categoriesValues, data[1], data[2], data[3], data[4], data[5], data[9])
        finalData.append(data)
    # after doing all the components calculate car rating
    finalRating = vehicleRatingWeightCalculus(categoriesValues)

    return (finalData, categoriesValues, finalRating)

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
    """Calculates the vehicle 5-grade rating part B"""

    weights = [0.5, 0.3, 0.15, 0.05]
    finalScore = 0
    adjusted_weights = []
    total_weight = 0
    values = [[0, 0], [0, 0], [0, 0], [0, 0]]
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

def vulbproba_security_feature(type):
    base_vulnProb = 1.0 # ECU unsecure and without security features
    min_vulnProb = 0.05 # ECU secure but it is impossible to have a 100% secure system
    enabled_features = [] # Features available implemented on the ECU

    if type == "manual":        
        for feature, value in SECURITY_FEATURES.items():
            if isinstance(value, dict): #mutual exclusion situation with sub-feature detected
                for sub_feature in value:
                    response = input(f"Is '{sub_feature}' enabled? (y/n): ").strip().lower()
                    if response == "y":
                        enabled_features.append(sub_feature)
                        break #mutual exclusion after first selection it jumps out.
            else:
                response = input(f"Is '{feature}' enabled? (y/n): ").strip().lower()
                if response == "y":
                    enabled_features.append(feature)
            
    elif type == "auto":
        for feature, value in SECURITY_FEATURES.items():
            if isinstance(value, dict): #mutual exclusion situation with sub-feature detected
                sub_features = list(value.keys()) 
                chosen_feature = random.choice([None] + sub_features)
                if chosen_feature:
                    enabled_features.append(chosen_feature) 
            else: 
                if random.choice([True, False]):
                    enabled_features.append(feature)
       
    for feature in enabled_features:
        base_vulnProb -= SECURITY_FEATURES.get(feature, 0)

        base_vulnProb = max(base_vulnProb, min_vulnProb)
        base_vulnProb = round(base_vulnProb, 2)

    print("Enabled features:", enabled_features)
    print("Vulnerability probability:", base_vulnProb)

    return base_vulnProb

def write_to_file_raw(data, seedValue, runNr, totalRuns, format="pickle"):
    """Write the raw data to a file, including seedValue, run number and total number of runs to do"""

    # each object has all the information
    objToWrite = [[seedValue, runNr, totalRuns], data]

    if format == "pickle":
        with open(FILENAME_RAW, "ab") as file_raw:
            pickle.dump(objToWrite, file_raw)

    elif format == "json":
        with open(FILENAME_RAW, mode="a", newline="", encoding="utf-8") as file_raw:
            # each line is a valid json object. The file itself will not be
            jsonObjStr = json.dumps(objToWrite, separators=(",", ":"))
            print(jsonObjStr, file=file_raw)

    else:  # any other format is bare
        with open(FILENAME_RAW, mode="a", newline="", encoding="utf-8") as file_raw:
            print(objToWrite, file=file_raw)

def write_to_file(data, categoriesValues, finalRating=0.0, seedValue=0, runNr=0, totalRuns=0):
    """Write the generated simulation data to a CSV file."""

    # write the raw data to a file
    write_to_file_raw(data, seedValue, runNr, totalRuns)

    file_exists = os.path.exists(FILENAME_RESULTS)

    with open(FILENAME_RESULTS, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")

        if not file_exists:
            # Define header for the CSV file
            writer.writerow(
                [
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
                    "Seed Value",
                    "Run Nr",
                    "Total nr of Runs",
                ]
            )  # Write the header row

        num = [0, 0, 0, 0]
        avg = [0.0, 0.0, 0.0, 0.0]
        std = [0.0, 0.0, 0.0, 0.0]
        med = [0.0, 0.0, 0.0, 0.0]
        summ = [0.0, 0.0, 0.0, 0.0]
        for i in range(len(num)):
            num[i] = len(categoriesValues[i])
            if num[i] > 0:
                summ[i] = sum(categoriesValues[i])
                avg[i] = summ[i] / num[i]
                std[i] = stdev(categoriesValues[i]) if num[i] > 1 else 0
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
                finalRating,
                seedValue,
                runNr,
                totalRuns,
            ]
        )

        print(f"Data written to {FILENAME_RESULTS}")

# TODO: get values from file to runit more times
def main():
    # Use argparse as described in
    # https://docs.python.org/3/howto/argparse.html#argparse-tutorial
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", help="the simulation type (auto or manual)", choices=["auto", "manual"])
    parser.add_argument("-n", "--runs", help="the number of times to run the simulation; greater than 0", type=int)
    parser.add_argument("-s", "--seed", help="the seed value to be set (0 to randomize seed)", type=int)
    args = parser.parse_args()

    type = args.type
    if not type:
        type = input("Choose the simulation type (auto or manual): ").strip()
    seedValue = args.seed
    if seedValue is None:  # can be 0, which is false
        seedValue = int(input("Enter seed value to be set (0 to randomize seed):"))

    if seedValue == 0:
        seedValue = random.randint(1, 10000)
    
    if type == "auto":
        nr_runs = args.runs
        if not nr_runs:  # cannot be zero
            nr_runs = int(input("How many times would you like to repeat the simulation: "))

        numberECUs = random.randint(0, 100)
        vulnProb = vulbproba_security_feature(type)
        maxVuln = round(random.uniform(0, 6.9), 1)
        minVuln = round(random.uniform(0, maxVuln), 1)

        domainWeight = [
            round(random.uniform(0, 1), 1),  # Type ADAS
            round(random.uniform(0, 1), 1),  # Type PowerTrain
            round(random.uniform(0, 1), 1),  # Type HMI
            round(random.uniform(0, 1), 1),  # Type Body
            round(random.uniform(0, 1), 1),  # Type Chassi
        ]
        safetyWeight = [
        round(random.uniform(0, 1), 1),  # Type QM
        round(random.uniform(0, 1), 1),  # Type A
        round(random.uniform(0, 1), 1),  # Type B
        round(random.uniform(0, 1), 1),  # Type C
        round(random.uniform(0, 1), 1),  # Type D
        ]
    elif type == "manual":
        nr_runs = args.runs
        if not nr_runs:  # cannot be zero
            nr_runs = int(input("How many times would you like to repeat the simulation: "))
        
        numberECUs = int(input("How many ECU's do you wish to simulate (e.g values between 0 and 100): "))
        vulnProb = vulbproba_security_feature(type)
        maxVuln = float(input("Maximum vulnerability score (e.g values between 0 and 6.9): "))
        minVuln = float(input("Minimum vulnerability score (e.g values between 0 and 6.9, must be less than maximum): "))
        domainWeight = [
            # Type ADAS
            float(input("Enter probability for generating components type ADAS (e.g values between 0 and 1):")),
            # Type PowerTrain
            float(input("Enter probability for generating components type PowerTrain (e.g values between 0 and 1):")),
            # Type HMI
            float(input("Enter probability for generating components type HMI (e.g values between 0 and 1):")),
            # Type Body
            float(input("Enter probability for generating components type Body (e.g values between 0 and 1):")),
            # Type Chassi
            float(input("Enter probability for generating components type Chassi (e.g values between 0 and 1):")),
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
    
    for nRun in range(nr_runs):
        categoriesValues = [[], [], [], []]  # reset in every run
        if type == "auto":  # randomize for each run
            vulnProb = round(random.uniform(0, 1), 1)

        (finalData, categoriesValues, finalRating) = generate_simulation_data(
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
        write_to_file(finalData, categoriesValues, finalRating, seedValue, nRun + 1, nr_runs)

if __name__ == "__main__":
    # Declaration and track of all of the vehicle 5-grade rating values
    main()
