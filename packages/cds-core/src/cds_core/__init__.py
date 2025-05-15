from pathlib import Path
import ipyvue
import re

from glue.config import settings

# Register any custom Vue components
comp_dir = Path(__file__).parent / "vue_components"


def load_custom_vue_components():
    for comp_path in comp_dir.rglob("*.vue"):
        if comp_path.is_file:
            comp_name = re.sub(r"(?<!^)(?=[A-Z])", "-", comp_path.stem).lower()
            ipyvue.register_component_from_file(
                name=comp_name,
                file_name=comp_path,
            )


# Override glue settings
settings.BACKGROUND_COLOR = "white"
settings.FOREGROUND_COLOR = "black"
