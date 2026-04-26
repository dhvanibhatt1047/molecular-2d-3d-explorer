# 🔬 Molecular 2D & 3D Explorer
**Advanced Level Project | Month 3 Final - Aparaitech Internship**

The **Molecular 2D & 3D Explorer** is a high-performance cheminformatics dashboard designed to bridge the gap between raw chemical data and interactive visualization. Built as the final milestone of my internship at **Aparaitech**, this tool enables researchers and students to search for chemical entities and instantly receive high-fidelity structural diagrams, hardware-accelerated 3D models, and real-time pharmacological analysis.

---

## 🚀 Key Features

### 1. **Interactive Visualization**
* **Precision 2D Diagrams:** High-fidelity chemical sketching generated via the **RDKit** engine.
* **Dynamic 3D Models:** Hardware-accelerated "Ball & Stick" simulations with smooth auto-rotation powered by **3Dmol.js**.

### 2. **Pharmacological Intelligence**
* **Lipinski Rule of 5:** Real-time evaluation of bioavailability. The dashboard dynamically highlights numeric values for Molecular Weight, LogP, H-Donors, and H-Acceptors in **Emerald Green** (Pass) or **Rose Red** (Fail).
* **Physicochemical Insights:** Instant calculation of **LogP (Solubility)** and **QED (Drug-Likeness)** with detailed text explanations.

### 3. **Smart Discovery Engine**
* **Persistent Discovery History:** Every analyzed molecule is saved to a local **SQLite3** database for instant, clickable retrieval from the sidebar.
* **Similar Analog Engine:** A background algorithm compares your search against your history using **Morgan Fingerprints** and **Tanimoto Similarity** to suggest structural relatives.

### 4. **Automated Reporting**
* **Unified PDF Export:** Generate professional scientific reports with one click via **jsPDF**.
* **Buffer Snapshot Technology:** Implements a specialized render-buffer capture to ensure live WebGL 3D models are embedded perfectly in reports without blank boxes.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python / Flask |
| **Chemistry Engine** | RDKit (C++ Core) |
| **Data Resolution** | PubChem API |
| **Database** | SQLite3 |
| **3D Rendering** | WebGL / 3Dmol.js |
| **Frontend** | Tailwind CSS / JavaScript (ES6+) |
| **Reporting** | jsPDF |

---

## 📦 Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/dhvanibhatt1047/molecular-2d-3d-explorer.git](https://github.com/dhvanibhatt1047/molecular-2d-3d-explorer.git)
    cd molecular-2d-3d-explorer
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```
    *Access the dashboard at `http://127.0.0.1:5000`*

---

## 📑 The Process (Project Logic)
1.  **Parsing:** The user enters a chemical name or formula which is resolved to a SMILES string via the **PubChem API**.
2.  **Calculation:** The **RDKit** backend sanitizes the molecule and computes physicochemical properties on the fly.
3.  **Persistence:** Data is committed to `molecules.db` to enable the persistent history and analog comparison features.
4.  **Reporting:** A custom JavaScript function forces a 3D re-render to populate the WebGL buffer, allowing for high-quality image extraction into the final PDF report.

---

## 📜 Acknowledgments
* **Aparaitech:** For providing the opportunity to work on this advanced-level internship project.
* **Team Leader:** For the constant technical guidance, support, and mentorship throughout this journey.

---
**Developed with ❤️ by Dhvani Bhatt**