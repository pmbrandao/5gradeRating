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

Once you have defined the configuration in the main() function:
  1. Run the simulation script.
  2. It will simulate a number of vehicles based on your numberECUs setting.
  3. After execution, a file named simulation.csv will be generated.

Each row in the file represents a vehicle's cybersecurity evaluation based on its components and simulated vulnerabilities.

### 📊 How to Analyze the Output Data

The simulator exports data in CSV format, but the initial view in Excel may not show columns properly aligned. To fix that:
#### ✅ Step 1 – Format Columns in Excel
  1. Open the simulation.csv file in Microsoft Excel.
  2. Go to Data → Text to Columns.
  3. Choose Delimited and click Next.
  4. Select Comma as the delimiter and click Finish.

💡 This will properly separate the data into columns for analysis.

![image](https://github.com/user-attachments/assets/2d8c56a9-d98e-4a63-9445-2aea2fae7c75)
![image](https://github.com/user-attachments/assets/c9068966-3b52-47fd-a803-142a71ec3e03)
![image](https://github.com/user-attachments/assets/72e56d69-59c5-4907-8592-a28cf562d608)

#### ✅ Step 2 – Visualize the Data
With the data formatted, you can now explore and visualize:
  - Sort by any column, such as final_rating, to compare vehicle cybersecurity levels.
  - Apply conditional formatting to visualize trends and highlight components or categories with higher vulnerability impact.

![image](https://github.com/user-attachments/assets/63a0e6b3-ddb8-4bf9-8bf3-c110bd0afe16)
SNIP
![image](https://github.com/user-attachments/assets/56f33f1b-8683-417c-b45a-5edf03665821)




