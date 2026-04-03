---
title: "amorphouspy"
excerpt: "End-to-end workflows for computational glass science — from structure generation and melt-quench simulations to property calculation and structural analysis."
collection: portfolio
---

**amorphouspy** is an open-source Python framework providing end-to-end workflows for atomistic simulations of oxide glasses. It covers the full pipeline from generating initial structural models through running molecular dynamics simulations with LAMMPS to computing material properties and performing detailed structural analysis.

**Role:** Lead developer  
**Collaborators:** BAM (Berlin), Schott AG, Max-Planck-Institute for Sustainable Materials (MPISsusMat)  
**GitHub:** TBD 

---

### Key Features

- **Structure Generation** — create random oxide glass structures from composition dicts (e.g., `{"SiO2": 75, "Na2O": 15, "CaO": 10}`) with automatic density estimation via Fluegel's empirical model
- **Interatomic Potentials** — built-in support for PMMCS (Pedone), BJP (Bouhadja), and SHIK (Sundararaman) force fields with automatic LAMMPS input generation
- **Melt-Quench Simulations** — multi-stage heating/cooling protocols with potential-specific temperature programs
- **Structural Analysis** — RDFs, coordination numbers, Qₙ distributions, bond angle distributions, ring statistics, cavity analysis
- **Property Calculation** — elastic moduli (stress-strain finite differences), viscosity (Green-Kubo), coefficient of thermal expansion (NPT fluctuations)
- **Visualization** — interactive Plotly-based plotting of all structural analysis results
- **REST API** — FastAPI-based service with MCP integration for workflow automation

---

### Install

```bash
curl -fsSL https://pixi.sh/install.sh | bash  # install pixi
git clone https://github.com/achrafatila/amorphouspy.git
cd amorphouspy && pixi install
```

---

**Requirements:** Python ≥ 3.11 | **License:** BSD 3-Clause
