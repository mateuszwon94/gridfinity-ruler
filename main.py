import argparse
from build123d import export_stl, export_step, export_gltf, export_brep, Mesher
from config import Config, parse_output_formats, parse_bed_size
from generate_ruler import generate_ruler


def main():
    # CLI help text and argument parsing
    help_epilog = """
=======================================================
           IMPORTANT NOTES FOR SLICING
=======================================================
1. COLOR SUPPORT: Formats like .step and .3mf retain the multicolor
   information (white body, black text/markers). The .stl file
   will load as a single, monochromatic object.
2. IMPORTING FILES: When importing a .step or .3mf file into modern
   slicers (like Bambu Studio, PrusaSlicer, or OrcaSlicer),
   the software may ask:
   'Load as a single object with multiple parts?'
   ---> ALWAYS SELECT 'YES' <---
   This ensures the ruler stays together and you can easily
   assign different filaments to the base and the text.
=======================================================
    """

    parser = argparse.ArgumentParser(
        description="Generate a multicolor, parametric Gridfinity ruler with dual scales.",
        epilog=help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-u", "--ruler-units", type=int, default=None,
                        help="How long the ruler should be in Gridfinity units. If omitted, the ruler will be sized to the maximum length that fits the printer bed.")
    parser.add_argument("-w", "--width-multiplier", type=float, default=0.5,
                        help="Ruler width as a multiplier of 1 length unit (default: 0.5)")
    parser.add_argument("-o", "--output", type=str, default="gridfinity_ruler",
                        help="Output file prefix without extension (default: 'gridfinity_ruler')")
    parser.add_argument("-f", "--output-format", type=parse_output_formats, default="all",
                        help="Output format: 'stl', 'step', '3mf', 'gltf', 'brep', 'all', or comma-separated list like 'stl,3mf' (default: 'all')")

    parser.add_argument("--unit-length", type=float, default=42.0,
                        help="1 standard Gridfinity length unit in mm (default: 42.0)")
    parser.add_argument("--unit-height", type=float, default=7.0,
                        help="1 standard Gridfinity height unit in mm (default: 7.0)")
    parser.add_argument("--base-thickness", type=float, default=2.0,
                        help="Total thickness of the ruler base in mm (default: 2.0)")
    parser.add_argument("--marker-extrusion", type=float, default=0.3,
                        help="How much the markers/text extrude above the top plane in mm (default: 0.6)")
    parser.add_argument("--chamfer-width", type=float, default=4.0,
                        help="Side chamfer width inward along the Y axis in mm (default: 4.0)")
    parser.add_argument("--chamfer-depth", type=float, default=1.0,
                        help="Side chamfer depth downward along the Z axis in mm (default: 1.0)")
    parser.add_argument("-b", "--bed-size", type=parse_bed_size, default="256x256",
                        help="Printer bed size in WIDTHxDEPTH format, e.g. '270x270' (default: 256x256)")
    parser.add_argument("-m", "--bed-margin", type=float, default=10.0,
                        help="Margin from the printer bed edge in mm on each side (default: 10.0)")
    parser.add_argument("--half-unit-labels", choices=["none", "half-only", "full"], default="none",
                        help="Half-unit label mode: none, half-only (.5), or full (7.5).")

    args = parser.parse_args()
    config = Config.from_args(args)

    # Generate the ruler model using parsed configuration
    multicolor_ruler = generate_ruler(config)

    # Check if the generated ruler fits on the bed and issue warning if it doesn't
    if not config.ruler_fits_on_bed():
        max_possible = config.get_max_ruler_length()
        print(f"\n⚠️  WARNING: The ruler ({config.ruler_length:.1f}mm) does NOT fit on the printer bed!")
        print(f"   Maximum possible length: {max_possible:.1f}mm ({max_possible / config.unit_length:.1f}U)")
        print(f"   Available bed: {config.bed_size[0]}x{config.bed_size[1]}mm with {config.bed_margin}mm margins")
        print()

    print(f"\n--- GENERATION INFO ---")
    print(f"Parameters used: Length={config.ruler_units}U, Width={config.width_multiplier}U ({config.ruler_width}mm), Base Thickness={config.base_thickness}mm, Extrusion={config.marker_extrusion}mm, Bed Size={config.bed_size_str}, Bed Margin={config.bed_margin}mm, Half-unit labels={config.half_unit_labels}")
    print(f"Target extensions generated: {config.output_format}")

    # Export generated model into requested formats
    if "stl" in config.output_format:
        stl_filename = f"{config.output}.stl"
        export_stl(multicolor_ruler, stl_filename)
        print(f"[+] Saved STL file: {stl_filename}")

    if "step" in config.output_format:
        step_filename = f"{config.output}.step"
        export_step(multicolor_ruler, step_filename)
        print(f"[+] Saved STEP file: {step_filename}")

    if "3mf" in config.output_format:
        mf_filename = f"{config.output}.3mf"
        exporter = Mesher()
        exporter.add_shape(multicolor_ruler)
        exporter.write(mf_filename)
        print(f"[+] Saved 3MF file: {mf_filename}")

    if "gltf" in config.output_format:
        gltf_filename = f"{config.output}.glb"
        export_gltf(multicolor_ruler, gltf_filename, binary=True)
        print(f"[+] Saved GLTF file: {gltf_filename}")

    if "brep" in config.output_format:
        brep_filename = f"{config.output}.brep"
        export_brep(multicolor_ruler, brep_filename)
        print(f"[+] Saved BREP file: {brep_filename}")

    print("\nGeneration completed successfully.")


if __name__ == "__main__":
    main()
