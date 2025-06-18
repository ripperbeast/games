
def find_valid_agi_ene_split_range(total_stat, agi_range, ene_range):
    best_match = None
    min_distance = float('inf')
    for agi_percent in range(agi_range[0], agi_range[1] + 1):
        ene_percent = 100 - agi_percent
        est_agi = int(total_stat * agi_percent / 100)
        est_ene = total_stat - est_agi
        for agi in range(0, total_stat + 1, 15):
            ene = total_stat - agi
            if ene % 36 == 0:
                distance = abs(agi - est_agi) + abs(ene - est_ene)
                if distance < min_distance:
                    min_distance = distance
                    best_match = (agi, ene)
    return best_match
