import argparse
from build123d import *

def parse_output_formats(value: str) -> list[str]:
    """
    Custom argparse type handler to parse comma-separated formats or 'all'.
    Validates input against supported file extensions.
    """
    val_lower = value.strip().lower()
    
    # Define currently supported extensions in the system
    supported_formats = ["stl", "step", "3mf", "gltf", "brep"]
    
    if val_lower == "all":
        return supported_formats
        
    # Split the string by commas and strip any accidental whitespace
    selected_formats = [f.strip().lower() for f in val_lower.split(",")]
    
    # Validate each parsed format
    for f in selected_formats:
        if f not in supported_formats:
            raise argparse.ArgumentTypeError(
                f"Unsupported format '{f}'. Supported formats are: "
                f"{', '.join(supported_formats)} or 'all'."
            )
            
    return selected_formats

# ==========================================
# CONFIGURATION MANAGEMENT CLASS
# ==========================================
class Config:
    def __init__(self, **kwargs):
        """
        Initialize the configuration with explicit values or defaults.
        Ensures output_format always resolves to a list of validated strings.
        """
        # Gridfinity system defaults
        self.u_len = kwargs.get("u_len", 42.0)
        self.u_height = kwargs.get("u_height", 7.0)
        
        # Ruler parameters
        self.ruler_u = kwargs.get("ruler_u", 8)
        self.width_multiplier = kwargs.get("width_multiplier", 0.5)
        self.base_thickness = kwargs.get("base_thickness", 2.0)
        self.marker_extrusion = kwargs.get("marker_extrusion", 0.3)
        
        # Chamfer parameters
        self.chamfer_width = kwargs.get("chamfer_width", 4.0)
        self.chamfer_depth = kwargs.get("chamfer_depth", 1.0)
        
        # Output parameters
        self.output = kwargs.get("output", "gridfinity_ruler")
        
        # Standardize output_format field to always be a list
        raw_format = kwargs.get("output_format", "all")
        if raw_format == "all":
            self.output_format = ["stl", "step", "3mf", "gltf", "brep"]
        elif isinstance(raw_format, list):
            self.output_format = raw_format
        elif isinstance(raw_format, str):
            self.output_format = [f.strip().lower() for f in raw_format.split(",")]
        else:
            self.output_format = [raw_format]

    @classmethod
    def from_args(cls, args):
        """
        Factory method to initialize the Config class directly 
        from the parsed command line arguments.
        """
        return cls(**vars(args))

    # Dynamic properties for calculated values (Read-only adapters)
    @property
    def ruler_length(self) -> float:
        """Calculate total physical length dynamically based on current units."""
        return self.ruler_u * self.u_len

    @property
    def ruler_width(self) -> float:
        """Calculate total physical width dynamically based on current multiplier."""
        return self.width_multiplier * self.u_len


def main():
    # ==========================================
    # ARGUMENT PARSING
    # ==========================================
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
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Primary parameters (with short single-letter flags)
    parser.add_argument("-u", "--ruler-u", type=int, default=8, 
                        help="How long the ruler should be in Gridfinity units (default: 8)")
    parser.add_argument("-w", "--width-multiplier", type=float, default=0.5, 
                        help="Ruler width as a multiplier of 1 length unit (default: 0.5)")
    parser.add_argument("-o", "--output", type=str, default="gridfinity_ruler", 
                        help="Output file prefix without extension (default: 'gridfinity_ruler')")
    parser.add_argument("-f", "--output-format", type=parse_output_formats, default="all",
                        help="Output format: 'stl', 'step', '3mf', 'gltf', 'brep', 'all', or comma-separated list like 'stl,3mf' (default: 'all')")

    # Advanced system and model parameters
    parser.add_argument("--u-len", type=float, default=42.0, 
                        help="1 standard Gridfinity length unit in mm (default: 42.0)")
    parser.add_argument("--u-height", type=float, default=7.0, 
                        help="1 standard Gridfinity height unit in mm (default: 7.0)")
    parser.add_argument("--base-thickness", type=float, default=2.0, 
                        help="Total thickness of the ruler base in mm (default: 2.0)")
    parser.add_argument("--marker-extrusion", type=float, default=0.3, 
                        help="How much the markers/text extrude above the top plane in mm (default: 0.6)")
    parser.add_argument("--chamfer-width", type=float, default=4.0, 
                        help="Side chamfer width inward along the Y axis in mm (default: 4.0)")
    parser.add_argument("--chamfer-depth", type=float, default=1.0, 
                        help="Side chamfer depth downward along the Z axis in mm (default: 1.0)")

    args = parser.parse_args()

    # ==========================================
    # INITIALIZE CONFIG OBJECT
    # ==========================================
    config = Config.from_args(args)

    # ==========================================
    # GEOMETRY GENERATION (Using Config Object)
    # ==========================================

    # --- PART 1: RULER BASE (COLOR: WHITE) ---
    with BuildPart() as base_ruler:
        with BuildSketch(Plane.YZ) as profile:
            Polygon([
                (-config.ruler_width/2, 0),
                (config.ruler_width/2, 0),
                (config.ruler_width/2, config.base_thickness - config.chamfer_depth),
                (config.ruler_width/2 - config.chamfer_width, config.base_thickness),
                (-config.ruler_width/2 + config.chamfer_width, config.base_thickness),
                (-config.ruler_width/2, config.base_thickness - config.chamfer_depth)
            ])
        extrude(amount=config.ruler_length)

    base_ruler.part.color = Color("White")

    # --- PART 2: MARKERS AND TEXT (COLOR: BLACK) ---
    with BuildPart() as markers:
        with BuildSketch(Plane.XY) as markers_sketch:
            
            # --- Length Scale (Top Edge, Y = RULER_WIDTH / 2) ---
            for i in range(0, config.ruler_u + 1):
                x = i * config.u_len
                
                # First marker: Half-triangle (right half), tip at (0,0)
                if i == 0:
                    with Locations((x, config.ruler_width/2)):
                        Polygon([(0, 0), (1.5, -3), (0, -3)], align=(Align.MIN, Align.MAX))
                    with Locations((x + 1, config.ruler_width/2 - 4)):
                        Text(str(i), font_size=6, align=(Align.MIN, Align.MAX))
                
                # Last marker: Half-triangle (left half), tip at (0,0)
                elif i == config.ruler_u:
                    with Locations((x, config.ruler_width/2)):
                        Polygon([(0, 0), (-1.5, -3), (0, -3)], align=(Align.MAX, Align.MAX))
                    with Locations((x - 1, config.ruler_width/2 - 4)):
                        Text(str(i), font_size=6, align=(Align.MAX, Align.MAX))
                
                # Middle markers: Full triangle, tip at (0,0)
                else:
                    with Locations((x, config.ruler_width/2)):
                        Polygon([(0, 0), (1.5, -3), (-1.5, -3)], align=(Align.CENTER, Align.MAX))
                    with Locations((x, config.ruler_width/2 - 4)):
                        Text(str(i), font_size=6, align=(Align.CENTER, Align.MAX))

            # Half-unit scale markers
            for i in range(1, config.ruler_u * 2):
                if i % 2 != 0:
                    x = i * (config.u_len / 2)
                    with Locations((x, config.ruler_width/2)):
                        Polygon([(0, 0), (1, -2), (-1, -2)], align=(Align.CENTER, Align.MAX))

            # --- Height Scale (Bottom Edge, Y = -RULER_WIDTH / 2) ---
            max_z_units = int(config.ruler_length // config.u_height)
            for i in range(0, max_z_units + 1):
                x = i * config.u_height
                
                # First marker: Half-triangle (right half), tip at (0,0)
                if i == 0:
                    with Locations((x, -config.ruler_width/2)):
                        Polygon([(0, 0), (1, 2), (0, 2)], align=(Align.MIN, Align.MIN))
                    with Locations((x + 1, -config.ruler_width/2 + 3)):
                        Text(str(i), font_size=4, align=(Align.MIN, Align.MIN))
                
                # Last marker: Half-triangle (left half), tip at (0,0)
                elif i == max_z_units:
                     with Locations((x, -config.ruler_width/2)):
                         Polygon([(0, 0), (-1, 2), (0, 2)], align=(Align.MAX, Align.MIN))
                     with Locations((x - 1, -config.ruler_width/2 + 3)):
                        Text(str(i), font_size=4, align=(Align.MAX, Align.MIN))
                
                # Middle markers: Full triangle, tip at (0,0)
                else:
                    with Locations((x, -config.ruler_width/2)):
                        Polygon([(0, 0), (1, 2), (-1, 2)], align=(Align.CENTER, Align.MIN))
                    with Locations((x, -config.ruler_width/2 + 3)):
                        Text(str(i), font_size=4, align=(Align.CENTER, Align.MIN))

        extrude(amount=config.base_thickness + config.marker_extrusion)

    markers.part.color = Color("Black")

    # ==========================================
    # COMBINATION AND FILE EXPORT
    # ==========================================
    multicolor_ruler = Compound([base_ruler.part, markers.part])
    
    print(f"\n--- GENERATION INFO ---")
    print(f"Parameters used: Length={config.ruler_u}U, Width={config.width_multiplier}U ({config.ruler_width}mm), Base Thickness={config.base_thickness}mm, Extrusion={config.marker_extrusion}mm")
    print(f"Target extensions generated: {config.output_format}")

    # STL EXPORT
    if "stl" in config.output_format:
        stl_filename = f"{config.output}.stl"
        export_stl(multicolor_ruler, stl_filename)
        print(f"[+] Saved STL file: {stl_filename}")
        
    # STEP EXPORT
    if "step" in config.output_format:
        step_filename = f"{config.output}.step"
        export_step(multicolor_ruler, step_filename)
        print(f"[+] Saved STEP file: {step_filename}")

    # 3MF EXPORT (Using Mesher)
    if "3mf" in config.output_format:
        mf_filename = f"{config.output}.3mf"
        exporter = Mesher()
        exporter.add_shape(multicolor_ruler)
        exporter.write(mf_filename)
        print(f"[+] Saved 3MF file: {mf_filename}")

    # GLTF EXPORT
    if "gltf" in config.output_format:
        gltf_filename = f"{config.output}.glb"
        export_gltf(multicolor_ruler, gltf_filename, binary=True)
        print(f"[+] Saved GLTF file: {gltf_filename}")

    # BREP EXPORT
    if "brep" in config.output_format:
        brep_filename = f"{config.output}.brep"
        export_brep(multicolor_ruler, brep_filename)
        print(f"[+] Saved BREP file: {brep_filename}")
        
    print("\nGeneration completed successfully.")

if __name__ == "__main__":
    main()
