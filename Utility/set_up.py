"""
This is a set up program that creates config.json and the necessary directories
in the file system.
"""
from os import makedirs
import json
from platformdirs import user_data_dir, user_config_dir, user_cache_dir

def create_dir(path: str) -> None:
    """
    A wrapper function of os.makedirs(path).
    Handling FileExistsError if the directory already exists.
    
    Parameters
    ----------
    path : str
        The directory to be created

    Returns
    -------
    None
    
    """
    try:
        makedirs(path)
    except FileExistsError:
        pass
    return

## Parameters
config: dict = {"app_name": "DeliverySystem",
                "project_name":"SE_Term_Project",
                "customer_suffix": "\\customer\\",
                "staff_suffix": "\\staff\\",
                "order_suffix": "\\order\\"
                }


## constructs the path string
data_dir = user_data_dir(config["app_name"], config["project_name"])
config_dir = user_config_dir(config["app_name"], config["project_name"])
cache_dir = user_cache_dir(config["app_name"], config["project_name"])

customer_dir = data_dir + config["customer_suffix"]
staff_dir = data_dir + config["staff_suffix"]
order_dir = data_dir + config["order_suffix"]

## create directories in local file system
create_dir(customer_dir)
create_dir(staff_dir)
create_dir(order_dir)

## Create config.json
with open("config.json", "w") as file:
    json.dump(config, file, indent=4)
    
## Testing
if __name__ == "__main__":
    print(config_dir)
    from pathlib import Path
    
    assert Path(customer_dir).is_dir()
    assert Path(staff_dir).is_dir()
    assert Path(order_dir).is_dir()
    
    
    

