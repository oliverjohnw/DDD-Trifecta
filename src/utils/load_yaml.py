from pathlib import Path

import yaml


def load_yaml(yaml_path: Path) -> dict:
    """
    Loads a YAML file from the given path.

    Args:
        yaml_path (Path): Path to the YAML file.

    Returns:
        dict: Loaded YAML content.
    """
    # yaml file path
    path = Path(yaml_path)

    # load file
    try:
        with path.open("r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise e
    except yaml.YAMLError as e:
        raise e