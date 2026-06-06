import argparse


def parse_output_formats(value: str) -> list[str]:
    """
    Custom argparse type handler to parse comma-separated formats or 'all'.
    Validates input against supported file extensions.
    """
    val_lower = value.strip().lower()
    
    supported_formats = ["stl", "step", "3mf", "gltf", "brep"]
    
    if val_lower == "all":
        return supported_formats
        
    selected_formats = [f.strip().lower() for f in val_lower.split(",")]
    
    for f in selected_formats:
        if f not in supported_formats:
            raise argparse.ArgumentTypeError(
                f"Unsupported format '{f}'. Supported formats are: "
                f"{', '.join(supported_formats)} or 'all'."
            )
            
    return selected_formats


class Config:
    def __init__(self, **kwargs):
        """
        Initialize the configuration with explicit values or defaults.
        Ensures output_format always resolves to a list of validated strings.
        """
        self.u_len = kwargs.get("u_len", 42.0)
        self.u_height = kwargs.get("u_height", 7.0)
        
        self.ruler_u = kwargs.get("ruler_u", 8)
        self.width_multiplier = kwargs.get("width_multiplier", 0.5)
        self.base_thickness = kwargs.get("base_thickness", 2.0)
        self.marker_extrusion = kwargs.get("marker_extrusion", 0.3)
        
        self.chamfer_width = kwargs.get("chamfer_width", 4.0)
        self.chamfer_depth = kwargs.get("chamfer_depth", 1.0)
        
        self.output = kwargs.get("output", "gridfinity_ruler")
        
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

    @property
    def ruler_length(self) -> float:
        return self.ruler_u * self.u_len

    @property
    def ruler_width(self) -> float:
        return self.width_multiplier * self.u_len
