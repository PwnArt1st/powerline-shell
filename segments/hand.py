def add_hand_segment(powerline):
    if not os.geteuid() == 0:
        hand = u' \U0001F449 '
    else:
        hand = u' \U0001F595 '
    powerline.append(hand, Color.HOSTNAME_FG, Color.HOSTNAME_BG)
