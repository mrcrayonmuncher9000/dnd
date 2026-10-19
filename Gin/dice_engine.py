import random

def roll_dice(dice_type: int, num_dice: int = 1, ability_modifier: int = 0, advantage_type: str = "None") -> dict:
    """
    Handles all the D&D dice logic and mathematical operations.
    Returns a dictionary containing raw rolls, final calculated total, and log string.
    """
    all_rolls = []
    
    # Core loop for rolling multiple dice
    for _ in range(num_dice):
        if advantage_type == "Advantage" and dice_type == 20:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            all_rolls.append(max(roll1, roll2))
        elif advantage_type == "Disadvantage" and dice_type == 20:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            all_rolls.append(min(roll1, roll2))
        else:
            all_rolls.append(random.randint(1, dice_type))
            
    # Calculate totals
    base_total = sum(all_rolls)
    final_total = base_total + ability_modifier
    
    return {
        "rolls": all_rolls,
        "final_total": final_total
    }
