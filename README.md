\#  FireScope – Kerala

\### Multi-Satellite Active Fire Detection, Harmonization and Analysis



\## 1. Introduction



FireScope is a satellite-based active fire detection and analysis project focused on Kerala, India. The project integrates active fire observations from multiple satellite platforms to explore fire detection patterns, compare satellite observations, and visualize the results through an interactive dashboard.



By combining MODIS and VIIRS data, FireScope provides a common platform for exploring satellite-based fire observations and understanding differences between satellite detection systems.



\## 2. Objectives



\- Integrate active fire observations from multiple satellite platforms.

\- Harmonize satellite datasets into a common data structure.

\- Explore spatial and temporal relationships between satellite detections.

\- Analyze Fire Radiative Power (FRP) differences.

\- Visualize fire detection patterns across Kerala.

\- Provide an interactive dashboard for filtering and exploring observations.



\## 3. Satellite Data Sources



FireScope uses active fire observations from:



| Satellite instrument | Satellite platform |

|---|---|

| MODIS | Aqua |

| MODIS | Terra |

| VIIRS | NOAA-20 |

| VIIRS | NOAA-21 |

| VIIRS | Suomi-NPP |



Data are obtained from NASA FIRMS (Fire Information for Resource Management System).



\## 4. Key Features



\- \*\*Multi-Satellite Data Integration:\*\* Combines MODIS and VIIRS observations.

\- \*\*Data Harmonization:\*\* Converts observations into a common dataset structure.

\- \*\*Spatial and Temporal Analysis:\*\* Explores relationships between detections based on geographic distance and acquisition time.

\- \*\*FRP Analysis:\*\* Examines differences in Fire Radiative Power across satellite platforms.

\- \*\*Interactive Map:\*\* Displays satellite fire detections across Kerala.

\- \*\*Data Visualization:\*\* Provides platform-wise, daily, monthly, and day/night analysis.

\- \*\*Filtering:\*\* Allows users to filter observations by satellite platform and matching status.

\- \*\*CSV Export:\*\* Allows users to download filtered detection records.



\## 5. Methodology



The project follows these major steps:



1\. Satellite Data Collection

2\. Kerala Boundary-Based Filtering

3\. Data Preprocessing

4\. Timestamp Preparation

5\. Multi-Satellite Data Integration

6\. Spatial and Temporal Matching

7\. Statistical Analysis

8\. Interactive Dashboard Development



\### Matching Criteria



The exploratory cross-platform matching process uses:



\- Maximum spatial distance: 500 metres

\- Maximum time difference: 60 minutes

\- Matching method: Mutual nearest-neighbour matching



These criteria identify potential relationships between observations. They do not confirm duplicate detections or represent verified individual fire events.



\## 6. Technologies Used



\*\*Programming and Data Analysis\*\*

\- Python

\- Pandas

\- NumPy

\- GeoPandas

\- Shapely

\- SciPy

\- Statsmodels

\- Scikit-learn



\*\*Backend\*\*

\- FastAPI

\- Uvicorn



\*\*Frontend\*\*

\- HTML

\- CSS

\- JavaScript

\- Leaflet.js

\- Chart.js



\## 7. Project Structure



```text

FireScope/

│

├── backend/

│   ├── app.py

│   └── data/

│

├── datasets/

│   ├── processed/

│   │   └── firescope\_harmonized.csv

│   └── geoBoundaries-IND-ADM1\_simplified.geojson

│

├── frontend/

│   └── index.html

│

├── requirements.txt

├── README.md

└── .gitignore

```



\## 8. Installation and Execution



\### Step 1: Clone the Repository



```bash

git clone https://github.com/Anusankarys/FireScope-Kerala.git

cd FireScope-Kerala

```



\### Step 2: Install Dependencies



```bash

pip install -r requirements.txt

```



\### Step 3: Start the Backend



From the project root directory, run:



```bash

uvicorn backend.app:app --reload

```



Backend URL:



http://127.0.0.1:8000



API documentation:



http://127.0.0.1:8000/docs



\### Step 4: Start the Frontend



Open another terminal:



```bash

cd frontend

python -m http.server 5500

```



Open the dashboard in your browser:



http://127.0.0.1:5500



Keep both backend and frontend terminals running while using the dashboard.



\## 9. Data Sources and References



\- NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/

\- geoBoundaries: https://www.geoboundaries.org/



Refer to the included geoBoundaries citation and use information file for boundary data attribution.



\## 10. Limitations



Satellite instruments have different spatial resolutions, detection sensitivities, and acquisition schedules. Therefore, differences in their observations should be considered when interpreting results.



Spatial and temporal matching identifies potential cross-platform relationships and should not be interpreted as confirmation of unique fire events or sensor accuracy.



\## 11. Future Scope



\- Integration of additional satellite data sources.

\- Near-real-time fire monitoring.

\- Advanced fire pattern analysis.

\- Improved visualization and reporting.

\- Expansion to additional geographical regions.



\## 12. Project Information



\*\*Project Name:\*\* FireScope – Kerala



\*\*Project Domain:\*\* Satellite Remote Sensing and Active Fire Analysis



\*\*Challenge:\*\* NASA Space Apps Challenge





