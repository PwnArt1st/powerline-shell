def add_hand_segment(powerline):
    if not os.geteuid() == 0:
        hand = u' \U0001F449 '
    else:
        hand = u' \U0001F595 '
    bg = Color.CMD_PASSED_BG
    fg = Color.CMD_PASSED_FG
    if powerline.args.prev_error != 0:
        fg = Color.CMD_FAILED_FG
        bg = Color.CMD_FAILED_BG
    powerline.append(hand, fg, bg)
