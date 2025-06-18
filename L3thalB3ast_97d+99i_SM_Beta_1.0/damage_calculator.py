
# === CONFIGURATION SECTION ===

# --- Optimizer Settings ---
agi_percent_min = 35
resets = 44
manual_agi = 0
manual_energy = 5760

# --- Item Setup ---
weapon_type = "Shining"         # "kundun" or "shining"
weapon_level = 11
weapon_add_str = "(+16)"
weapon_opt = False
weapon_lvl20 = False

pendant_opt = True
pendant_lvl20 = False

wings_level = 11
wings_add_str = "(+16)"

satan_source = "satan"          # "satan", "dynorant", or ""
monster_name = "Mega Crust"

# === FUNCTIONS ===

import math
from stats_generator import find_valid_agi_ene_split_range

# Automatically assign required strength based on weapon type
def get_required_strength(weapon_type):
    return {
        "shining": 398,
        "kundun": 334
    }.get(weapon_type.lower(), 0)

def calculate_total_stat_points(resets, base_points=66, level=349, level_point_gain=5, reset_point_gain=430):
    return base_points + (resets * reset_point_gain) + (level * level_point_gain)

def get_raw_energy_base(energy):
    return energy / 9, energy / 4

def calculate_base_wiz_damage(raw_min, raw_max, weapon_opt, pendant_opt, weapon_lvl20=False, pendant_lvl20=False):
    multiplier = 1.0
    bonus_min = bonus_max = 0
    if weapon_opt: multiplier *= 1.02
    if pendant_opt: multiplier *= 1.02
    if weapon_lvl20: bonus_min += 17; bonus_max += 17
    if pendant_lvl20: bonus_min += 17; bonus_max += 17
    return raw_min * multiplier + 45 + bonus_min, raw_max * multiplier + 67 + bonus_max

def apply_flat_adds(min_dmg, max_dmg, weapon_add, wings_add):
    return min_dmg + weapon_add + wings_add, max_dmg + weapon_add + wings_add

def calculate_bracket_bonus(max_dmg, weapon_percent):
    return math.floor(max_dmg * weapon_percent / 100)

def apply_final_multipliers(min_dmg, max_dmg, satan_percent, wings_percent):
    def apply(dmg):
        return math.floor(dmg * (1 + satan_percent / 100) * (1 + wings_percent / 100))
    return apply(min_dmg), apply(max_dmg)

def get_weapon_percent_from_level(level, weapon_type="kundun"):
    weapon_type = weapon_type.lower()
    tables = {
        "kundun": {0: 81, 1: 84, 2: 88, 3: 91, 4: 95, 5: 98, 6: 102, 7: 105, 8: 109, 9: 112, 10: 117, 11: 121},
        "shining": {0: 98, 1: 101, 2: 105, 3: 108, 4: 112, 5: 115, 6: 119, 7: 122, 8: 126, 9: 129, 10: 134, 11: 138}
    }
    return tables.get(weapon_type, {}).get(level, 0)

def get_valid_flat_weapon_add(flat_str):
    return {"(+0)": 0, "(+4)": 4, "(+8)": 8, "(+12)": 12, "(+16)": 16}.get(flat_str, 0)

def get_wings_percent_from_level(level):
    return 32 + level if 0 <= level <= 11 else 32

def get_valid_flat_wings_add(flat_str):
    return {"(+0)": 0, "(+4)": 4, "(+8)": 8, "(+12)": 12, "(+16)": 16}.get(flat_str, 0)

def apply_monster_defense_reduction(min_dmg, max_dmg, monster_def, satan_percent, wings_percent):
    def apply(dmg):
        base = max(0, math.floor(dmg - monster_def))
        after_satan = math.floor(base * (1 + satan_percent / 100))
        return math.floor(after_satan * (1 + wings_percent / 100))
    return apply(min_dmg), apply(max_dmg)

def calculate_excellent_with_multipliers(max_dmg, monster_def, satan_percent, wings_percent):
    total_def_multiplier = (1 + satan_percent / 100) * (1 + wings_percent / 100)
    return max(0, math.floor(max_dmg * 1.2 - monster_def * total_def_multiplier))

def get_monster_defense(monster_name):
    return {
        "Mega Crust": 240, "Alpha Crust": 410, "Spirit Sorcerer BC6": 500,
        "Spirit Knight BC6": 450, "Spirit Beast BC6": 400, "Orc Archer": 170,
        "Orc Warrior": 190, "Bloody Wolf": 200, "Force Warrior": 190,
        "Iron Wheel": 230, "Beam Knight": 270
    }.get(monster_name, 0)

def get_satan_percent(source):
    return {"satan": 30, "dynorant": 15}.get(source, 0)

# === MAIN EXECUTION ===
def main():
    strength = get_required_strength(weapon_type)

    # Determine if optimizer is enabled
    optimizer_enabled = agi_percent_min != 0
    if not optimizer_enabled:
        print("⚠️ Optimizer disabled. Manual stats will be used.")
        print("ℹ️  Set 'agi_percent_min' to a non-zero value to enable stat optimization.")
    total_points = calculate_total_stat_points(resets)
    optimized = False

    if optimizer_enabled:
        agi_percent_max = min(agi_percent_min + 1, 99)
        agi_range = (agi_percent_min, agi_percent_max)
        ene_range = (100 - agi_percent_max, 100 - agi_percent_min)

        for offset in range(50):
            str_candidate = strength + offset
            total_stat_pool = total_points - str_candidate
            result = find_valid_agi_ene_split_range(total_stat_pool, agi_range, ene_range)
            if result:
                agi, energy = result
                strength = str_candidate
                optimized = True
                break

    if optimized:
        print(f"✅ Optimized Split: STR={strength}, AGI={agi}, ENE={energy}")
    else:
        agi = manual_agi
        energy = manual_energy
        print("❌ No valid optimized AGI/ENE split found.")
        print(f"⚠️  Using fallback values → STR={strength}, AGI={agi}, ENE={energy}")

    raw_min, raw_max = get_raw_energy_base(energy)
    no_weapon_min = math.floor(raw_min + 45)
    no_weapon_max = math.floor(raw_max + 67)

    base_min, base_max = calculate_base_wiz_damage(
        raw_min, raw_max, weapon_opt, pendant_opt, weapon_lvl20, pendant_lvl20
    )

    weapon_percent = get_weapon_percent_from_level(weapon_level, weapon_type)
    flat_weapon_add = get_valid_flat_weapon_add(weapon_add_str)
    wings_percent = get_wings_percent_from_level(wings_level)
    flat_wings_add = get_valid_flat_wings_add(wings_add_str)

    panel_min, panel_max = apply_flat_adds(base_min, base_max, flat_weapon_add, flat_wings_add)

    bracket_bonus = calculate_bracket_bonus(panel_max, weapon_percent) if weapon_percent else 0
    total_min = math.floor(panel_min) + bracket_bonus
    total_max = math.floor(panel_max) + bracket_bonus

    print(f"{weapon_type} Staff {weapon_level}/{flat_weapon_add}, Wings {wings_level}/{flat_wings_add}")
    print(f"Panel Damage: {round(panel_min)} ~ {round(panel_max)}", end='')
    if bracket_bonus:
        print(f" (+{bracket_bonus})")
    else:
        print()

    satan_percent = get_satan_percent(satan_source)
    monster_def = get_monster_defense(monster_name)

    final_min, final_max = apply_final_multipliers(total_min, total_max, satan_percent, wings_percent)
    excellent_final = calculate_excellent_with_multipliers(final_max, monster_def, satan_percent, wings_percent)
    reduced_min, reduced_max = apply_monster_defense_reduction(total_min, total_max, monster_def, satan_percent, wings_percent)

    print(f"Damage vs {monster_name}: (Crit: {reduced_max}) (Excellent: {excellent_final})")


if __name__ == "__main__":
    main()
