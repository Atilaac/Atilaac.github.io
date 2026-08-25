---
title: "amorphouspy"
excerpt: "End-to-end workflows for computational glass science — structure generation, melt-quench simulations, property calculation, structural analysis, and a job API that exposes the whole pipeline to LLM agents."
collection: portfolio
---

**amorphouspy** is an open-source Python framework for atomistic simulations of oxide glasses. It covers the full pipeline from generating initial structural models, through running molecular dynamics with LAMMPS, to computing material properties and performing detailed structural analysis. A companion package, `amorphouspy_api`, strings those functions into end-to-end workflows with [executorlib](https://executorlib.readthedocs.io/) and exposes them as web endpoints — including an MCP server, so an LLM-powered agent can drive the simulations directly.

**Role:** Lead developer — core framework, structural analysis, interatomic potentials  
**Collaborators:** BAM (Berlin), SCHOTT AG, Max Planck Institute for Sustainable Materials (MPI-SusMat)  
**GitHub:** [github.com/glasagent/amorphouspy](https://github.com/glasagent/amorphouspy)  
**Documentation:** [glasagent.github.io/amorphouspy](https://glasagent.github.io/amorphouspy/)  
**DOI:** [10.5281/zenodo.19553302](https://doi.org/10.5281/zenodo.19553302)

---

### Key Features

**`amorphouspy` — the simulation library**

- **Structure Generation** — build random oxide glass structures from composition dicts (e.g. `{"SiO2": 75, "Na2O": 15, "CaO": 10}`) with automatic density estimation via Fluegel's empirical model
- **Interatomic Potentials** — PMMCS (Pedone), BJP (Bouhadja), SHIK (Sundararaman), Du/Teter (with optional three-body term), BMP (Bertani–Menziani–Pedone, harmonic and screened-harmonic) and Yang2026 force fields, with automatic LAMMPS input generation and selectable Coulomb summation (Ewald, PPPM, Wolf, DSF)
- **Melt-Quench Simulations** — multi-stage, potential-specific temperature programs with ensemble control and a unified pre-equilibration stage
- **Structural Analysis** — RDFs and coordination numbers, projected RDFs, Qₙ distributions with bridging/non-bridging oxygen classification, network connectivity, bond angle distributions, Guttmann ring statistics, cavity analysis, and static structure factors *S(q)* — parallelized and averageable over trajectory frames
- **Property Calculations** — elastic moduli (stress–strain finite differences), viscosity (Green–Kubo, with VFT fitting), coefficient of thermal expansion (temperature scan or NPT fluctuations), and self-diffusion coefficients from the MSD with Arrhenius fitting
- **LAMMPS I/O** — read dump trajectories back as ASE `Atoms` with frame slicing and striding, and automatic element mapping

**`amorphouspy_api` — the workflow service**

- **End-to-end Workflows** — submit a composition, get back the glass structure and its predicted properties; steps run as a dependency graph on HPC resources through executorlib
- **Job Management API** — submit, monitor, tag, search and cancel jobs, with a results database and downloadable structures and trajectories
- **Materials Layer** — `/glasses` endpoints to browse, look up and search computed properties across completed jobs, including nearest-composition matching
- **Agent Access** — an MCP server exposing the workflows as tools, so an LLM agent can run and interpret simulations
- **Visualization** — interactive Plotly views of structure, melt-quench, elastic, viscosity and CTE results, served straight from a job

---

### Install

```bash
pip install amorphouspy          # or: conda install -c conda-forge amorphouspy
```

For development, or to run the API and workflow layer:

```bash
curl -fsSL https://pixi.sh/install.sh | bash   # install pixi
git clone https://github.com/glasagent/amorphouspy.git
cd amorphouspy && pixi install
```

---

### Quick Start

```python
from amorphouspy import analyze_structure, generate_potential, get_ase_structure, get_structure_dict, melt_quench_simulation

structure_dict = get_structure_dict({"SiO2": 75, "Na2O": 15, "CaO": 10}, target_atoms=3000)
atoms = get_ase_structure(structure_dict)
potential = generate_potential(structure_dict, potential_type="pmmcs")

result = melt_quench_simulation(structure=atoms, potential=potential, temperature_high=5000.0, temperature_low=300.0, cooling_rate=1e12)

data, sem = analyze_structure(result["structure"])   # mean and standard error
print(f"Density: {data.density:.3f} g/cm³")
print(f"Network connectivity: {data.network.connectivity:.2f}")
```

---

**Requirements:** Python ≥ 3.12, LAMMPS | **License:** Apache-2.0

Supported by the [Federal Ministry of Research, Technology and Space](https://www.bmftr.bund.de/EN) through the [GlasAgent MaterialDigital project](https://www.materialdigital.de/project/28).
