import argparse
from build123d import *

def main():
    # ==========================================
    # MULTILINE EPILOG FOR THE HELP MENU
    # ==========================================
    help_epilog = """
=======================================================
           IMPORTANT NOTES FOR SLICING
=======================================================
1. COLOR SUPPORT: Only the .step format retains the multicolor
   information (white body, black text/markers). The .stl file
   will load as a single, monochromatic object.
2. IMPORTING .STEP: When importing the .step file into modern
   slicers (like Bambu Studio, PrusaSlicer, or OrcaSlicer),
   the software will ask:
   'Load as a single object with multiple parts?'
   ---> ALWAYS SELECT 'YES' <---
   This ensures the ruler stays together and you can easily
   assign different filaments to the base and the text.
=======================================================
    """

    parser = argparse.ArgumentParser(
        description="Generate a multicolor, parametric Gridfinity ruler with dual scales.",
        epilog=help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Primary parameters (assigned with short single-letter flags for quick CLI usage)
    parser.add_argument("-u", "--ruler-u", type=int, default=8, 
                        help="How long the ruler should be in Gridfinity units (default: 8)")
    parser.add_argument("-w", "--width-multiplier", type=float, default=0.5, 
                        help="Ruler width as a multiplier of 1 length unit (default: 0.5)")
    parser.add_argument("-o", "--output", type=str, default="gridfinity_ruler", 
                        help="Output file prefix without extension (default: 'gridfinity_ruler')")
    parser.add_argument("-f", "--format", type=str, choices=['stl', 'step', 'both'], default='both',
                        help="Output file format: 'stl', 'step', or 'both' (default: 'both')")

    # Advanced system and model parameters
    parser.add_argument("--u-len", type=float, default=42.0, 
                        help="1 standard Gridfinity length unit in mm (default: 42.0)")
    parser.add_argument("--u-height", type=float, default=7.0, 
                        help="1 standard Gridfinity height unit in mm (default: 7.0)")
    parser.add_argument("--base-thickness", type=float, default=2.0, 
                        help="Total thickness of the ruler base in mm (default: 2.0)")
    parser.add_argument("--marker-extrusion", type=float, default=0.6, 
                        help="How much the markers/text extrude above the top plane in mm (default: 0.6)")
    parser.add_argument("--chamfer-width", type=float, default=4.0, 
                        help="Side chamfer width inward along the Y axis in mm (default: 4.0)")
    parser.add_argument("--chamfer-depth", type=float, default=1.0, 
                        help="Side chamfer depth downward along the Z axis in mm (default: 1.0)")

    args = parser.parse_args()

    # ==========================================
    # PARAMETER ASSIGNMENT & CALCULATIONS
    # ==========================================
    U_LEN = args.u_len
    U_HEIGHT = args.u_height
    RULER_U = args.ruler_u
    WIDTH_MULTIPLIER = args.width_multiplier
    BASE_THICKNESS = args.base_thickness
    MARKER_EXTRUSION = args.marker_extrusion
    CHAMFER_WIDTH = args.chamfer_width
    CHAMFER_DEPTH = args.chamfer_depth
    
    RULER_LENGTH = RULER_U * U_LEN
    RULER_WIDTH = WIDTH_MULTIPLIER * U_LEN

    # ==========================================
    # GEOMETRY GENERATION (Multicolor Split)
    # ==========================================

    # --- PART 1: RULER BASE (COLOR: WHITE) ---
    with BuildPart() as base_ruler:
        with BuildSketch(Plane.YZ) as profile:
            Polygon([
                (-RULER_WIDTH/2, 0),
                (RULER_WIDTH/2, 0),
                (RULER_WIDTH/2, BASE_THICKNESS - CHAMFER_DEPTH),
                (RULER_WIDTH/2 - CHAMFER_WIDTH, BASE_THICKNESS),
                (-RULER_WIDTH/2 + CHAMFER_WIDTH, BASE_THICKNESS),
                (-RULER_WIDTH/2, BASE_THICKNESS - CHAMFER_DEPTH)
            ])
        extrude(amount=RULER_LENGTH)

    base_ruler.part.color = Color("White")


    # --- PART 2: MARKERS AND TEXT (COLOR: BLACK) ---
    with BuildPart() as markers:
        # IN MODERN BUILD123D API (v0.8+): We pass the plane directly to BuildSketch
        with BuildSketch(Plane.XY.offset(BASE_THICKNESS - CHAMFER_DEPTH)) as markers_sketch:
            
            # --- Length Scale (Top Edge, Y = RULER_WIDTH / 2) ---
            for i in range(0, RULER_U + 1):
                x = i * U_LEN
                if i == 0:
                    Polygon([(x, RULER_WIDTH/2), (x + 3, RULER_WIDTH/2), (x, RULER_WIDTH/2 - 3)])
                    with Locations((x + 1, RULER_WIDTH/2 - 4)):
                        Text(str(i), font_size=6, align=(Align.MIN, Align.MAX))
                elif i == RULER_U:
                    Polygon([(x - 3, RULER_WIDTH/2), (x, RULER_WIDTH/2), (x, RULER_WIDTH/2 - 3)])
                    with Locations((x - 1, RULER_WIDTH/2 - 4)):
                        Text(str(i), font_size=6, align=(Align.MAX, Align.MAX))
                else:
                    Polygon([(x - 1.5, RULER_WIDTH/2), (x + 1.5, RULER_WIDTH/2), (x, RULER_WIDTH/2 - 3)])
                    with Locations((x, RULER_WIDTH/2 - 4)):
                        Text(str(i), font_size=6, align=(Align.CENTER, Align.MAX))

            # Half-unit scale markers
            for i in range(1, RULER_U * 2):
                if i % 2 != 0:
                    x = i * (U_LEN / 2)
                    Polygon([(x - 1, RULER_WIDTH/2), (x + 1, RULER_WIDTH/2), (x, RULER_WIDTH/2 - 2)])

            # --- Height Scale (Bottom Edge, Y = -RULER_WIDTH / 2) ---
            max_z_units = int(RULER_LENGTH // U_HEIGHT)
            for i in range(0, max_z_units + 1):
                x = i * U_HEIGHT
                if i == 0:
                    Polygon([(x, -RULER_WIDTH/2), (x + 2, -RULER_WIDTH/2), (x, -RULER_WIDTH/2 + 2)])
                    with Locations((x + 1, -RULER_WIDTH/2 + 3)):
                        Text(str(i), font_size=4, align=(Align.MIN, Align.MIN))
                elif i == max_z_units:
                     Polygon([(x - 2, -RULER_WIDTH/2), (x, -RULER_WIDTH/2), (x, -RULER_WIDTH/2 + 2)])
                     with Locations((x - 1, -RULER_WIDTH/2 + 3)):
                        Text(str(i), font_size=4, align=(Align.MAX, Align.MIN))
                else:
                    Polygon([(x - 1, -RULER_WIDTH/2), (x + 1, -RULER_WIDTH/2), (x, -RULER_WIDTH/2 + 2)])
                    with Locations((x, -RULER_WIDTH/2 + 3)):
                        Text(str(i), font_size=4, align=(Align.CENTER, Align.MIN))

        extrude(amount=CHAMFER_DEPTH + MARKER_EXTRUSION)

    markers.part.color = Color("Black")

    # ==========================================
    # COMBINATION AND FILE EXPORT
    # ==========================================
    multicolor_ruler = Compound([base_ruler.part, markers.part])
    
    print(f"--- GENERATION INFO ---")
    print(f"Parameters used: Length={RULER_U}U, Width={WIDTH_MULTIPLIER}U ({RULER_WIDTH}mm), Base Thickness={BASE_THICKNESS}mm, Extrusion={MARKER_EXTRUSION}mm")
    
    if args.format in ['stl', 'both']:
        stl_filename = f"{args.output}.stl"
        # NOWE API BUILD123D: Globalna funkcja export_stl
        export_stl(multicolor_ruler, stl_filename)
        print(f"[+] Saved STL file: {stl_filename}")
        
    if args.format in ['step', 'both']:
        step_filename = f"{args.output}.step"
        # NOWE API BUILD123D: Globalna funkcja export_step
        export_step(multicolor_ruler, step_filename)
        print(f"[+] Saved STEP file: {step_filename}")

if __name__ == "__main__":
    main()