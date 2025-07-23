![ResearchGate](https://img.shields.io/badge/ResearchGate-Patrick%20Gruemer-blue?link=https://www.researchgate.net/profile/Patrick-Gruemer?ev=prf_overview)
![Automotive Project](https://img.shields.io/badge/Automotive-Project-blue)
[![Python 3.12.2](https://img.shields.io/badge/python-3.12.2-blue.svg)](https://www.python.org/downloads/release/python-3122/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Cybersecurity Researcher](https://img.shields.io/badge/Role-Cybersecurity%20Researcher-blue)

# 🛡️ Automotive Cybersecurity Maturity Assessment Framework

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <img src="car.png" alt="car" width="220" height="220">
  </a>

A Python-based implementation of a five-grade maturity model for assessing cybersecurity capabilities in the automotive sector, grounded in the methodologies from:

- 📄 [An Automotive Cybersecurity Maturity Level Assessment Programme (2023)](https://www.researchgate.net/publication/372140215)
- 📄 [Computing an Automotive Cybersecurity Maturity Level Assessment Programme (2024)](https://www.researchgate.net/publication/376231070)

---

## 🚀 Overview
Cybersecurity will be key for the new and future vehicles that depend on the exchange of data with the infrastructure. These vehicles will bring countless new features and are potentially capable of autonomous driving. This repository provides a simulator based on the research outlined above, with the primary goal of enabling users to simulate the five-grade rating framework designed to assess the cybersecurity quality of future vehicles and their components. The objective is to establish a trustable and reliable environment for these advanced technologies. Based on the standards used for secure software development and security assessment we defined a procedure for the evaluation of security of the technological components of a car.

## 🧠 High-level view of the 5-grade framework

![image](https://github.com/user-attachments/assets/1dd12d54-c210-4cbb-a520-4dcfd454195c)

## 📦 Installation
```bash
git clone https://github.com/paagrumer/5gradeRating
python simulator.py
```

## 📁 File Structure
```bash
├── simulator.py                # CLI entry point
├── README.md
```

## 🚗 Simulator Configuration and Usage Guide
### 🔧 Configuration Parameters
Before running the simulation, you can configure the following parameters:

```python
numberECUs        # Number of ECUs (Electronic Control Units) per vehicle
vulnProb          # Probability of a vulnerability occurring in a component
categoriesValues  # Importance weights for each category
maxVuln           # Maximum value for vulnerabilities per component
minVuln           # Minimum value for vulnerabilities per component

adasWeight        # ADAS system weight chance
powertWeight      # Powertrain weight chance 
hmiWeight         # Human-Machine Interface weight chance
bodyWeight        # Body Electronics weight chance
chWeight          # Chassis weight chance
qmWeight          # Quality Management weight chance

aWeight           # Safety level ASIL A weight chance
bWeight           # Safety level ASIL B weight chance
cWeight           # Safety level ASIL C weight chance
dWeight           # Safety level ASIL D weight chance
```

### ▶️ Running the Simulator

After configuring your simulation environment in the main() function (see example below):

**Example of default data:**

<img width="367" height="251" alt="image" src="https://github.com/user-attachments/assets/949b7d2c-52c0-4d63-8a0b-4f0fb3ddec1c" />

Follow these steps to run the 5-grade system simulator:

1. Execute the simulation script using the command:
  ```bash
   python simulador.py -t auto -s 100 -n 5000
   ```

   **Parameters:**
   - `-t`: Simulation type — `auto` or `manual`
   - `-n`: Number of simulation runs (must be > 0)
   - `-s`: Seed value for reproducibility (`0` for a randomized seed)

2. The simulation will generate data representing various 5-grade vehicle instances under the defined configuration.
3. Upon completion, a file named `simulation.csv` will be created. This file serves as the primary output for post-simulation analysis.

Each row in the file represents a vehicle's cybersecurity evaluation based on its components and simulated vulnerabilities.

### 📊 How to Analyze the Output Data

The simulator exports data in CSV format, but the initial view in Excel may not show columns properly aligned. To fix that:

#### ✅ Step 1 – Format Columns in Excel
  1. Open the `simulation.csv` file in Microsoft Excel.
  2. Navigate to the **Data** tab and click **Text to Columns**.
  3. Choose **Delimited** and click **Next**.
  4. Select **Comma** as the delimiter, then click **Finish**.

💡 This will properly separate the data into columns for analysis.

<img width="1296" height="182" alt="image" src="https://github.com/user-attachments/assets/f21862a2-1381-4050-9b9a-970164b64890" />
<img width="1298" height="310" alt="image" src="https://github.com/user-attachments/assets/599b4fce-9670-45f3-abd7-977b4aa15775" />
<img width="497" height="407" alt="image" src="https://github.com/user-attachments/assets/37f37a04-d939-4692-bcb2-ad7dacd31f81" />
<img width="497" height="405" alt="image" src="https://github.com/user-attachments/assets/d3099d9c-732a-47f1-9058-40dda0e71e6e" />

#### ✅ Step 2 – Visualize the Data
With the data correctly formatted, you can now explore and analyze it using Excel's built-in features:
  - **Sort** by columns such as `final_rating` to compare cybersecurity levels across vehicles.
  - Use **Conditional Formatting** to identify patterns and highlight components or categories with higher vulnerability impact.
  - **Play around with the data** to observe how different configurations, vulnerabilities, and component combinations influence the overall vehicle rating.

You can **repeat the simulation** as often as needed to explore alternative outcomes—just ensure you're using the same initial configuration, especially the **seed value**, to guarantee reproducibility.

<img width="1603" height="197" alt="image" src="https://github.com/user-attachments/assets/7fea9a28-a980-4591-a619-07de98e8d1bc" />
**SNIP**
<img width="1567" height="325" alt="image" src="https://github.com/user-attachments/assets/2652b5d9-e564-435a-91c1-56704645ece3" />
