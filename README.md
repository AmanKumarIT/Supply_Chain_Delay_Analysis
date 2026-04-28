# Supply Chain Disruption Intelligence System
**CORE_INTEL_V.04**

An advanced, AI-powered "Self-Healing" Supply Chain command center. This system monitors global logistics networks, predicts shipment delays using Machine Learning (XGBoost), and dynamically recalculates optimal shipping routes around disruptions using Graph Algorithms (Neo4j/NetworkX).

![Supply Chain Dashboard Preview](https://img.shields.io/badge/UI-Cyber_Architect-00F2FF?style=for-the-badge) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)

## ✨ Key Features

*   **Intelligent Rerouting (Graph Theory):** Utilizes Neo4j and NetworkX to represent the supply chain network as a complex graph. When disruptions occur, the system automatically calculates the most efficient alternative paths.
*   **AI Delay Prediction (Machine Learning):** An XGBoost regression model analyzes real-time stress variables (Weather/Thermal Stress, Traffic/Network Load, Congestion) to accurately predict potential delays and compute a comprehensive "Risk Score".
*   **"Cyber-Architect" Futuristic Interface:** A 100% bespoke, Pure Vanilla CSS frontend. Features glowing neon typography, pulsing holographic HUD (Heads-Up Display) modules, terminal log outputs, and custom grid geometries—completely independent of external CSS frameworks like Tailwind.
*   **Holographic Map Tracking:** Integrates Leaflet maps with custom CSS filtering (`invert`, `hue-rotate`, `grayscale`) to transform standard OpenStreetMap tiles into a deep-space, neon radar sweep visualization.
*   **Resilient Backend Architecture:** FastAPI backend designed with graceful degradation; if the Neo4j database goes offline, the system seamlessly falls back to local in-memory mock network data to ensure continuous operation.

## 🏗 Architecture & Tech Stack

### Frontend (Command Center)
*   **Framework:** React 19 + Vite
*   **Styling:** Pure Vanilla CSS (`index.css`) featuring custom CSS variables, keyframe animations, and glassmorphism.
*   **Mapping:** `react-leaflet` & `leaflet`
*   **HTTP Client:** Axios

### Backend (Intelligence Engine)
*   **Framework:** FastAPI (Python)
*   **Machine Learning:** `xgboost`, `scikit-learn`, `pandas`
*   **Graph Processing:** `neo4j` driver, `networkx`
*   **Data Models:** `pydantic`

---

## 🚀 How to Run the Project Locally

This project is separated into two main directories: `/backend` and `/frontend`. You will need to run both concurrently.

### 1. Start the Backend (FastAPI)

Ensure you have Python installed (Python 3.9+ recommended).

```bash
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload
```
*The backend will be available at `http://localhost:8000`. You can access the auto-generated Swagger documentation at `http://localhost:8000/docs`.*

*(Note: The system requires Neo4j to be running on `bolt://localhost:7687` for live graph operations. If Neo4j is not available, the `GraphService` will automatically utilize a hardcoded mock dataset so you can still test the application.)*

### 2. Start the Frontend (React UI)

Ensure you have Node.js installed.

```bash
cd frontend

# Install Node modules
npm install

# Start the Vite development server
npm run dev
```
*The frontend will be available at `http://localhost:5173`.*

---

## 💻 Usage Guide

1.  **Open the Command Center:** Navigate to `http://localhost:5173` in your browser.
2.  **Configure Route:** Use the HUD dropdowns on the left to select a **Source Node** (e.g., Delhi) and a **Target Node** (e.g., Chennai).
3.  **Apply Stress Variables:**
    *   Adjust the **Thermal Stress (Weather)** slider to simulate severe weather conditions (0.0 to 1.0).
    *   Adjust the **Network Load (Traffic)** slider to simulate port congestion and shipping bottlenecks (0.0 to 1.0).
4.  **Initialize Sweep:** Click the glowing `INITIALIZE SWEEP` button.
5.  **Analyze Telemetry:** 
    *   The XGBoost model will return an **Estimated Latency (Delay in Hours)** and a **Risk Score (0-100)**.
    *   The **Pulse Wave Visualizer** will animate based on the active scan.
    *   The **Terminal Log** will output the precise reason for the delay and recommend an action (e.g., `STANDBY` or `REROUTE`).
6.  **View Holographic Map:** If the Risk Score exceeds the safety threshold, the system will trigger a `REROUTE` action. The recommended new path will be instantly visualized in red on the glowing Leaflet radar map.

---

## 🎨 UI Aesthetic Guidelines: "The Kinetic Blueprint"

The frontend was designed with a strict adherence to the "Cyber-Architect" design philosophy:
*   **The Void:** Backgrounds are deep `#050505` and `#131313`.
*   **Neon Pulses:** Primary interactions glow in `#00F2FF` (Cyan), while alerts and data stress utilize `#fe00fe` (Magenta) and `#fbff6b` (Yellow).
*   **No Rounded Corners:** All components use `0px` border-radius to maintain a sharp, aggressive, machine-cut appearance.
*   **Tonal Layering:** Depth is created not through drop shadows, but by layering slightly lighter surface containers and applying subtle ambient glows to the borders.
