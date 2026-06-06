from build123d import *
from tqdm import tqdm


def generate_ruler(config):
    """Build and return the multicolor ruler model using the provided config."""
    
    # Calculate how many progress steps to show while generating markers
    total_length_markers = config.ruler_u + 1
    total_half_markers = config.ruler_u
    max_z_units = int(config.ruler_length // config.u_height)
    total_height_markers = max_z_units + 1
    total_steps = total_length_markers * 2 + total_half_markers + total_height_markers * 2

    # --- PART 1: RULER BASE (COLOR: WHITE) ---
    with BuildPart() as base_ruler:
        with BuildSketch(Plane.YZ) as profile:
            Polygon([
                (-config.ruler_width / 2, 0),
                (config.ruler_width / 2, 0),
                (config.ruler_width / 2, config.base_thickness - config.chamfer_depth),
                (config.ruler_width / 2 - config.chamfer_width, config.base_thickness),
                (-config.ruler_width / 2 + config.chamfer_width, config.base_thickness),
                (-config.ruler_width / 2, config.base_thickness - config.chamfer_depth),
            ])
        extrude(amount=config.ruler_length)

    base_ruler.part.color = Color("White")

    # --- PART 2: MARKERS AND TEXT (COLOR: BLACK) ---
    with tqdm(total=total_steps, bar_format="Generating [{bar}] {percentage:3.0f}% {postfix}", ascii=True, ncols=90) as progress:
        with BuildPart() as markers:
            with BuildSketch(Plane.XY) as markers_sketch:
                
                # --- Length Scale (Top Edge, Y = RULER_WIDTH / 2) ---
                for i in range(0, config.ruler_u + 1):
                    x = i * config.u_len
                    progress.set_postfix_str(f"Length scale {i} elements")
                    
                    # First marker: Half-triangle (right half), tip at (0,0)
                    if i == 0:
                        with Locations((x, config.ruler_width / 2)):
                            Polygon([(0, 0), (1.5, -3), (0, -3)], align=(Align.MIN, Align.MAX))
                        progress.update(1)

                        with Locations((x + 1, config.ruler_width / 2 - 4)):
                            Text(str(i), font_size=6, align=(Align.MIN, Align.MAX))
                        progress.update(1)
                    
                    # Last marker: Half-triangle (left half), tip at (0,0)
                    elif i == config.ruler_u:
                        with Locations((x, config.ruler_width / 2)):
                            Polygon([(0, 0), (-1.5, -3), (0, -3)], align=(Align.MAX, Align.MAX))
                        progress.update(1)

                        with Locations((x - 1, config.ruler_width / 2 - 4)):
                            Text(str(i), font_size=6, align=(Align.MAX, Align.MAX))
                        progress.update(1)
                    
                    # Middle markers: Full triangle, tip at (0,0)
                    else:
                        with Locations((x, config.ruler_width / 2)):
                            Polygon([(0, 0), (1.5, -3), (-1.5, -3)], align=(Align.CENTER, Align.MAX))
                        progress.update(1)

                        with Locations((x, config.ruler_width / 2 - 4)):
                            Text(str(i), font_size=6, align=(Align.CENTER, Align.MAX))
                        progress.update(1)

                # Half-unit scale markers
                for i in range(1, config.ruler_u * 2):
                    if i % 2 != 0:
                        x = i * (config.u_len / 2)
                        progress.set_postfix_str(f"Length scale {i/2} elements")
                        with Locations((x, config.ruler_width / 2)):
                            Polygon([(0, 0), (1, -2), (-1, -2)], align=(Align.CENTER, Align.MAX))
                        progress.update(1)

                # --- Height Scale (Bottom Edge, Y = -RULER_WIDTH / 2) ---
                for i in range(0, max_z_units + 1):
                    x = i * config.u_height
                    progress.set_postfix_str(f"Height scale {i} elements")
                    
                    # First marker: Half-triangle (right half), tip at (0,0)
                    if i == 0:
                        with Locations((x, -config.ruler_width / 2)):
                            Polygon([(0, 0), (1, 2), (0, 2)], align=(Align.MIN, Align.MIN))
                        progress.update(1)

                        with Locations((x + 1, -config.ruler_width / 2 + 3)):
                            Text(str(i), font_size=4, align=(Align.MIN, Align.MIN))
                        progress.update(1)
                    
                    # Last marker: Half-triangle (left half), tip at (0,0)
                    elif i == max_z_units:
                        with Locations((x, -config.ruler_width / 2)):
                            Polygon([(0, 0), (-1, 2), (0, 2)], align=(Align.MAX, Align.MIN))
                        progress.update(1)

                        with Locations((x - 1, -config.ruler_width / 2 + 3)):
                            Text(str(i), font_size=4, align=(Align.MAX, Align.MIN))
                        progress.update(1)
                    
                    # Middle markers: Full triangle, tip at (0,0)
                    else:
                        with Locations((x, -config.ruler_width / 2)):
                            Polygon([(0, 0), (1, 2), (-1, 2)], align=(Align.CENTER, Align.MIN))
                        progress.update(1)

                        with Locations((x, -config.ruler_width / 2 + 3)):
                            Text(str(i), font_size=4, align=(Align.CENTER, Align.MIN))
                        progress.update(1)

            extrude(amount=config.base_thickness + config.marker_extrusion)

        markers.part.color = Color("Black")

    # Combine base and markers into a single compound object for export
    return Compound([base_ruler.part, markers.part])
