# William Kavanagh, Feb 2019
# Generate a pure adversarial strategy for a player in CAG.
# USAGE: run(["K","A","K","W"], 2, "tmp", False)

# Main proc:
# Input: chars as list, player as <int> [1,2], file_prefix as str, always_p1 as bool
# Output: prints adversarial strategy for player <player> based on files <file_prefix>.tra/.sta
# Use the always_p1 flag to ensure strategy is always generated for player 1 (used for CAG processing)
def run(characters, player, file_prefix, always_p1):
    player_print = player
    if always_p1:
        player_print = 1
    print("//Action decision for P" + str(player_print) + ", adversarial strategy")
    reset_stuns_string = "(p" + str(player_print) + "_stun' = 0);"
    transitions = {}                                                            # Dictionary stores all relevant transitions
    for line in open(file_prefix+".tra","r").readlines():                       # For every line in the .tra file
        if line[-10:-2] == "p" + str(player) + "_turn_":                        # If the line is relevant
            transitions[line.split(" ")[0]] = line.split("_")[2][:-1]           # Store state_id with attack label
    state_description = ["attack", "turn", "p1c1", "p1c2", "p1_stun", "p2c1", "p2c2", "p2_stun"]
    flipped_description = ["attack", "turn", "p2c1", "p2c2", "p2_stun", "p1c1", "p1c2", "p1_stun"]
    for line in open(file_prefix+".sta","r").readlines()[1:]:                   # For every state in the model (skip first line)
        if line.split(":(")[1][0] != "0":                                       # If the state is a decision state
            break                                                               # States no longer relevant, end.
        if line.split(":(")[1][2] == str(player):                               # State is decision state for correct player
            state_info = line.split(":(")[1][:-2].split(",")                    # Collect state info as list (attack and turn, we know those)
            state_id = line.split(":(")[0]                                      # Collect state id
            if state_id in transitions.keys():                                  # If state is valid (states where the game is over are ignored)
                action_int = transitions[state_id]
                if always_p1 and player == 2 and int(action_int) < 9:           # If we need to translate an action for player 1 from player 2...
                    action_int = str(int(action_int) - 4)                       # Translate the action (i.e. p2c1 -> p1c1 becomes p1c1 -> p2c1, or 5 becomes 1)
                    guard_comm = "\t[p" + str(player_print) + "_turn_" + action_int + "]\t"    # build guard_comm string
                    for i in range(len(state_description)):                         # Iterate over each VAR in the state
                        if state_description[i] == "turn" and always_p1:
                            guard_comm += "turn = 1"
                        else:
                            guard_comm += flipped_description[i] + " = " + state_info[i]
                        if i < len(state_description) - 1:
                            guard_comm += " & "
                    guard_comm += " ->\n\t\t\t\t (attack' = " + action_int + ") & " + reset_stuns_string
                    print(guard_comm)
                else:
                    guard_comm = "\t[p" + str(player_print) + "_turn_" + action_int + "]\t"    # build guard_comm string
                    for i in range(len(state_description)):                         # Iterate over each VAR in the state
                        if state_description[i] == "turn" and always_p1:
                            guard_comm += "turn = 1"
                        else:
                            guard_comm += state_description[i] + " = " + state_info[i]
                        if i < len(state_description) - 1:
                            guard_comm += " & "
                    guard_comm += " ->\n\t\t\t\t (attack' = " + action_int + ") & " + reset_stuns_string
                    print(guard_comm)
    skip_action = "\t[p" + str(player_print) + "_turn_skip]\tattack = 0 & turn = "
    skip_action += str(player_print) + " & ( (p" + str(player_print) + "_stun = 1 & p" + str(player_print) + "c2 < 1) | "
    skip_action += "(p" + str(player_print) + "_stun = 2 & p" + str(player_print) + "c1 < 1) ) ->\n\t\t\t\t(attack' = 9) & "
    print(skip_action + reset_stuns_string + " // skip if forced")
