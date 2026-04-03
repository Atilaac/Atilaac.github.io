---
title: "atomex"
excerpt: "Python package for analyzing atomistic simulation and experimental data"
collection: portfolio
---

**atomex** is an open-source Python package providing a unified interface for analyzing data from molecular dynamics simulations and experimental techniques. To be shared publicly soon.

**Role:** Sole developer and maintainer

**Install:** `pip install atomex`  
**GitHub:** [github.com/Atilaac/atomex](https://github.com/Atilaac/atomex)


---

### Key Features

- to be announced later

---

### Quick Start

```python
from ase.io import read
from atomex.simulations import compute_rdf

frames = read("trajectory.xyz", index=":")
r, rdfs, cn = compute_rdf(frames, r_max=8.0)

# g(r) for Si–O pairs
g_SiO = rdfs[(8, 14)]
```

---

**Requirements:** Python ≥ 3.12 | **License:** BSD 3-Clause
