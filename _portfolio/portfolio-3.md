---
title: "journalfig"
excerpt: "Publication-ready matplotlib themes for twelve scientific publishers — exact column widths, compliant fonts, one string to retarget a figure."
collection: portfolio
---

**journalfig** is an open-source matplotlib theme package for **Nature**, **APS** (PRB/PRL), **Elsevier** (Acta Materialia, JNCS), **IOP**, **AIP**, **ACS**, **RSC**, **IEEE**, **PLOS**, **Wiley**, **PNAS**, and **Science**. Import once, then retarget a figure to a different journal by changing one string. Every number in the themes is traceable to a publisher document, with the six derived values marked as such.

**Role:** Sole developer and maintainer

**Install:** `pip install journalfig`  
**GitHub:** [github.com/Atilaac/journalfig](https://github.com/Atilaac/journalfig)  
**Documentation:** [aatila.com/journalfig](https://aatila.com/journalfig/)

---

### Key Features

- **Twelve publisher themes** — column widths, fonts, base sizes, panel-label style and raster dpi taken from each publisher's own author guide
- **Exact figure sizes** — `jf.subplots` / `jf.figure` pin the requested width in millimetres, bypassing the backend rounding and `bbox="tight"` cropping that quietly break it
- **Compliance checking** — `jf.check(fig)` reports font substitutions, text below the publisher minimum, thin lines and un-rasterized vector artists before submission
- **Multi-panel layouts** — `jf.mosaic` and `jf.gridspec` for panels of unequal size, with `jf.panel_labels` lettering them in reading order
- **One call to save** — `jf.save` writes PDF + SVG + PNG (TIFF and EPS on request) and warns when nothing written is a format the publisher accepts as final artwork
- **Accessible colours** — Okabe–Ito palette paired with line styles, identical across themes, so retargeting never changes colours and figures survive greyscale printing

---

### Quick Start

```python
import journalfig as jf

jf.use("elsevier")                                   # or "nature", "aps", "PRB", "Acta Materialia"
fig, ax = jf.subplots("elsevier", width="single")    # exact 90 mm, no figsize boilerplate
ax.plot(q, sq, label=r"$S(q)$")
ax.set_xlabel(r"$q$ (Å$^{-1}$)")
ax.legend()
jf.save(fig, "fig_structure_factor")                 # writes .pdf + .svg + .png
```

---

**Requirements:** Python ≥ 3.12, matplotlib ≥ 3.8 | **License:** MIT
