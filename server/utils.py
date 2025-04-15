

def check_config(config, config_check_list:list):
    """
    Check if the configuration contains all required keys.
    """
    for key in config_check_list:
        if key not in config:
            return False
    return True