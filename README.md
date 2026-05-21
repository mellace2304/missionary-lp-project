# Missionary LP Project

Optimal allocation of missionaries to unreached people groups in India using Linear Programming 

## Project Overview

This project uses Operations Research techniques to solve the missionary allocation problem: given a set of unreached people groups across Indian districts and a limited number of missionaries, how can we optimally allocate missionaries to maximize coverage of unreached populations?

The project consists of three main components:
1. **Data Scraping** - Collects people group and population data from Joshua Project
2. **Linear Programming** - Optimizes missionary allocation using Google OR-Tools
3. **Map Visualization** - Visualizes the allocation results on an interactive map

## Project Structure

```
Missionary-LP-Project/
├── Data Scraping/
│   ├── DataScraping.py          # Web scraper for Joshua Project data
│   ├── data.txt                 # Raw HTML data from Joshua Project
│   └── ALL_DATA.csv             # Dataset from scraping
│
├── Linear Programming/
│   ├── LP.py                    # Optimization solver
│   ├── missionary_allocation_results_realid.csv  # Allocation results
│   └── people_group_coverage_unreached_new.csv   # Coverage analysis
│
├── Map Visualization/
│   ├── MissionaryMap.html       # Interactive map visualization
│   ├── ammap.js                 # AnyMap library
│   ├── indiaDistrictsLowStates.js  # Map data for India districts
│   └── [map styles and data]
│
├── README.md                    # This file
├── requirements.txt             # Dependencies
└── Honors Petition.docx         # Project documentation
```

## Components

### 1. Data Scraping (`Data Scraping/`)

The data scraper collects information about unreached people groups across Indian districts from the Joshua Project website.

**Features:**
- Extracts URLs from Joshua Project maps
- Scrapes district-level population data
- Parses people group information
- Outputs structured CSV data

**Usage:**
```bash
cd "Data Scraping"
python DataScraping.py
```

**Output:** CSV files containing state, district, people group, population, and Christian population data.

### 2. Linear Programming Solver (`Linear Programming/`)

Uses Google OR-Tools to solve the missionary allocation optimization problem.

**Problem Definition:**
- **Objective:** Maximize coverage of unreached populations
- **Constraints:** 
  - Limited number of missionaries available
  - Each missionary can reach up to 10,000 people
  - Geographic and people group considerations
- **Variables:** Number of missionaries to allocate to each district/people group

**Usage:**
```bash
cd "Linear Programming"
python LP.py
```

**Requirements:**
- pandas
- numpy
- ortools

**Outputs:**
- `missionary_allocation_results_realid.csv` - Detailed allocation results
- `people_group_coverage_unreached_new.csv` - Coverage analysis

### 3. Map Visualization (`Map Visualization/`)

Creates an interactive HTML map showing missionary allocations across Indian districts.

**Usage:**
1. Open `MissionaryMap.html` in a web browser
2. View the distribution of missionaries across districts
3. Hover over districts to see allocation details

**Technologies:**
- AnyMap (AMMap) for interactive mapping
- District-level geographic boundaries for India
- Interactive tooltips and legends

## Installation

### Prerequisites
- Python 3.7+
- pip or conda for package management

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

## Workflow

1. **Run Data Scraping** (`DataScraping.py`)
   - Collects people group and population data
   - Generates `ALL_DATA.csv`

2. **Run Optimization** (`LP.py`)
   - Reads `ALL_DATA.csv`
   - Solves the allocation problem
   - Outputs results CSV files

3. **View Results** (`MissionaryMap.html`)
   - Open in web browser to visualize allocations
   - Explore geographic distribution

## Data Files

- **ALL_DATA.csv** - Master dataset containing:
  - State, District
  - People Group name and characteristics
  - Population and Christian population counts
  - Unreached population calculations

- **missionary_allocation_results_realid.csv** - Optimization results showing:
  - District allocations
  - Number of missionaries assigned
  - Coverage statistics

- **people_group_coverage_unreached_new.csv** - Coverage analysis:
  - People group coverage percentages
  - Unreached population tracking

## Key Metrics

- **Missionary Reach:** 10,000 people per missionary (configurable)
- **Focus:** Unreached people groups (non-Christian populations)
- **Geographic Scope:** Indian districts
- **Optimization Method:** Linear Programming (Google OR-Tools)

## Output Interpretation

The outputs provide:
1. **Which districts** should receive missionaries
2. **How many missionaries** each district should receive
3. **Estimated coverage** for each people group
4. **Geographic visualization** of the allocation

This helps organizations make data-driven decisions about missionary deployment.

## Notes

- Data sourced from Joshua Project (joshuaproject.net)
- Results are based on available census data and people group statistics
- Allocations assume uniform missionary effectiveness across regions
- Can be extended with additional constraints (language, cultural factors, etc.)

## License

The MIT License (MIT)

Copyright (c) 2026 Isaiah Mellace

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

## Contact

For any questions about this project, please email inmellace@liberty.edu 