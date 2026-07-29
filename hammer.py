"""
Returns a list of every end, and which team (a or b) had hammer
"""
def hammer_ends_list(a,b,lsfe) -> list:
    hammer_list = []
    for end in range(len(a)):
        # If start of game, check LSFE
        if end == 0:
            hammer = 'a' if lsfe == 1 else 'b'
        else:
            # If hammer team scored last end, switch hammer
            if hammer == 'a' and a[end-1] != 0:
                hammer = 'b'
            elif hammer == 'b' and b[end-1] != 0:
                hammer = 'a'
        hammer_list.append(hammer)
    return hammer_list


