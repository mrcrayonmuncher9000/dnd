ATTRIBUTES_LIST = [
    "None",
    "Strength",
    "Dexterity",
    "Constitution",
    "Intelligence",
    "Wisdom",
    "Charisma"
]

def format_attribute_log(attribute_name: str, modifier_value: int) -> str:
    """
    Example output: "+Dexterity(0)" or "" if None.
    """
    if not attribute_name or attribute_name.lower() == "none":
        return ""
    
    sign = "+" if modifier_value >= 0 else ""
    return f" {sign}{attribute_name}({modifier_value})"
