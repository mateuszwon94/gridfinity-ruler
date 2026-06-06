# Parametric Gridfinity Ruler Generator

A Python-based Code-CAD utility using `build123d` to generate configurable Gridfinity rulers with dual scales and multi-part color-aware exports.

## What it does

This tool creates a parametric Gridfinity ruler that can be exported in multiple CAD/file formats. It supports:

- Dynamic ruler length in Gridfinity units (`-u/--ruler-units`).
- Automatic maximum-length fitting when the unit count is omitted.
- Customizable width, base thickness, marker extrusion, chamfer width, and chamfer depth.
- Printer bed constraints via `--bed-size WIDTHxDEPTH` and `--bed-margin MM`.
- Dual scales: top edge for Gridfinity length units and bottom edge for Gridfinity height units.
- Optional half-unit labels using `--half-unit-labels none|half-only|full`.
- Multi-part color export for `.step` and `.3mf` so slicers can preserve the white body and black markers/text.

## Supported formats

- `stl`
- `step`
- `3mf`
- `gltf` (`.glb` binary output)
- `brep`

Use `-f all` or a comma-separated list like `-f stl,3mf`.

## Usage

```bash
python main.py -u 4 -w 0.5 -f step,3mf -b 270x270 -m 10 --half-unit-labels full -o gridfinity_ruler
```

If `--ruler-units` is omitted, the ruler will automatically be sized to the longest whole Gridfinity length that fits the specified print bed after margins.

## Important slicing notes

- `.step` and `.3mf` exports are intended to retain separate color/material information for the ruler body and markers.
- `.stl` is a single monochrome mesh and will not preserve multi-material colors.
- When importing `.step` or `.3mf` into slicers such as OrcaSlicer, Bambu Studio, or PrusaSlicer, choose the option to import as a single multi-part assembly if prompted.

## Current CLI options

- `-u, --ruler-units`: Number of Gridfinity length units.
- `-w, --width-multiplier`: Ruler width as a multiplier of one length unit.
- `-o, --output`: Output file prefix.
- `-f, --output-format`: Supported formats: `stl`, `step`, `3mf`, `gltf`, `brep`, `all`.
- `--unit-length`: Gridfinity unit length (default 42.0 mm).
- `--unit-height`: Gridfinity unit height (default 7.0 mm).
- `--base-thickness`: Base thickness in mm (default 2.0 mm).
- `--marker-extrusion`: Text/marker extrusion height in mm (default 0.3 mm).
- `--chamfer-width`: Chamfer width on the long edge in mm (default 4.0 mm).
- `--chamfer-depth`: Chamfer depth in mm (default 1.0 mm).
- `-b, --bed-size`: Printer bed size as `WIDTHxDEPTH` in mm (default `256x256`).
- `-m, --bed-margin`: Margin from the bed edge in mm on each side (default `10.0`).
- `--half-unit-labels`: `none`, `half-only`, or `full`.

## Notes on current behavior

- The ruler base is built in white and the markers/text are built in black.
- If the ruler would exceed the printer bed, the program still generates the model but prints a warning with the maximum possible fit length.
- `.gltf` output is currently saved as `binary .glb`.

## TODO

- Add explicit ASCII/binary export mode for supported file types, especially STL and GLTF, and for other formats where the underlying exporter supports both representations.
- Add a `--scale` or `--model-scale` option for consistent unit conversion and easier exporter handling.
- Improve `3mf` export so the part grouping is preserved in slicers that require assembly loading.
- Add a preview or validation step to report the exact fit orientation for the chosen bed size.
- Add an option to generate a ruler with colored filament zones or split-part geometry for dual-extrusion printing.
- Support a dedicated `--output-directory` folder path.
- Add a configuration file mode so defaults can be stored outside the command line.
