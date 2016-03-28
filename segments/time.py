def add_time_segment(powerline):
    if powerline.args.shell == 'bash':
        time = ' \xF0\x9F\x95\x91  \\t '
    elif powerline.args.shell == 'zsh':
        time = ' %* '
    else:
        import time
        time = ' %s ' % time.strftime('%H:%M:%S')

    powerline.append(time, Color.HOSTNAME_FG, Color.HOSTNAME_BG)
