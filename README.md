# Parametric Gridfinity Ruler Generator

A Python-based Code-CAD utility utilizing the `build123d` library to generate custom, ergonomic, and multi-color rulers tailored for the **Gridfinity** organization system.

## Features

- **Fully Parametric:** Easily adjust the ruler length (in Gridfinity U), width multipliers, base thickness, and chamfer profiles via command-line arguments.
- **Dual-Sided Scale:** - One side features standard Gridfinity length units (42mm) and half-units (21mm) with triangular markers and numerical labeling.
  - The opposite side features Gridfinity height units (7mm) with dedicated numerical markers.
- **Multicolor Ready:** Generates multi-part `.step` files with native color assignments (White body, Black text/markers) for seamless multi-material slicing in Bambu Studio, PrusaSlicer, or OrcaSlicer.
- **Clean CLI Interface:** User-friendly Command Line Interface with intuitive short flags (`-u`, `-w`, `-o`, `-f`) and a built-in `--help` documentation menu.
- **Print-Optimized Geometry:** Includes specialized edge clipping for start/end markers to ensure zero overhangs and perfect alignment with the ruler's physical boundaries.