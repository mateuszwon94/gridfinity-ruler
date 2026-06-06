import argparse
import math


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


def parse_bed_size(value: str) -> tuple[int, int]:
    """
    Parse a printer bed size in the format WIDTHxDEPTH, e.g. '270x270'.
    """
    normalized = value.strip().lower()
    parts = normalized.split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            "Printer bed size must be in format WIDTHxDEPTH, e.g. '270x270'."
        )

    try:
        width = int(parts[0])
        depth = int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Printer bed dimensions must be integers, e.g. '270x270'."
        )

    if width <= 0 or depth <= 0:
        raise argparse.ArgumentTypeError(
            "Printer bed dimensions must be positive integers."
        )

    return width, depth


class Config:
    def __init__(self, **kwargs):
        """
        Initialize the configuration with explicit values or defaults.
        Ensures output_format always resolves to a list of validated strings.
        """
        self.unit_length = kwargs.get("unit_length", 42.0)
        self.unit_height = kwargs.get("unit_height", 7.0)
        
        self.ruler_units = kwargs.get("ruler_units")
        self.width_multiplier = kwargs.get("width_multiplier", 0.5)
        self.base_thickness = kwargs.get("base_thickness", 2.0)
        self.marker_extrusion = kwargs.get("marker_extrusion", 0.3)
        
        self.chamfer_width = kwargs.get("chamfer_width", 4.0)
        self.chamfer_depth = kwargs.get("chamfer_depth", 1.0)
        
        self.output = kwargs.get("output", "gridfinity_ruler")
        self.bed_size = kwargs.get("bed_size", (256, 256))
        self.bed_margin = kwargs.get("bed_margin", 10.0)

        if self.ruler_units is None:
            self.ruler_units = self.compute_max_ruler_units()
        
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

    def compute_max_ruler_units(self) -> int:
        """Compute the maximum whole Gridfinity units that fit on the printer bed."""
        avail_width = self.bed_size[0] - 2 * self.bed_margin
        avail_depth = self.bed_size[1] - 2 * self.bed_margin

        if avail_width <= 0 or avail_depth <= 0:
            raise ValueError(
                f"Printer bed size too small after applying {self.bed_margin:.1f}mm margins on each side."
            )

        rect_width = self.ruler_width
        if rect_width > min(avail_width, avail_depth):
            raise ValueError(
                f"Ruler width {rect_width:.1f}mm does not fit within the available print area "
                f"{avail_width}x{avail_depth}mm after margins."
            )

        max_length = self._max_rectangle_length(avail_width, avail_depth, rect_width)
        max_units = int(math.floor(max_length / self.unit_length))

        if max_units < 1:
            raise ValueError(
                "Printer bed is too small to fit a single Gridfinity length unit."
            )

        return max_units

    @staticmethod
    def _max_rectangle_length(avail_width: float, avail_depth: float, rect_width: float) -> float:
        """Find the maximum length of a rectangle of given width that fits in the available box."""
        def length_for(theta: float) -> float:
            c = math.cos(theta)
            s = math.sin(theta)
            if c < 1e-9:
                return avail_depth if rect_width <= avail_width else 0.0
            if s < 1e-9:
                return avail_width if rect_width <= avail_depth else 0.0
            x = (avail_width - rect_width * s) / c
            y = (avail_depth - rect_width * c) / s
            return min(x, y) if x >= 0 and y >= 0 else 0.0

        best_theta = 0.0
        best_length = 0.0
        for step in range(1001):
            theta = step * math.pi / 2000
            length = length_for(theta)
            if length > best_length:
                best_length = length
                best_theta = theta

        low = max(0.0, best_theta - 0.02)
        high = min(math.pi / 2, best_theta + 0.02)
        for _ in range(20):
            t1 = low + (high - low) / 3
            t2 = high - (high - low) / 3
            if length_for(t1) > length_for(t2):
                high = t2
            else:
                low = t1

        return max(best_length, length_for((low + high) / 2))

    @property
    def ruler_length(self) -> float:
        return self.ruler_units * self.unit_length

    @property
    def ruler_width(self) -> float:
        return self.width_multiplier * self.unit_length

    @property
    def bed_size_str(self) -> str:
        return f"{self.bed_size[0]}x{self.bed_size[1]}"
