
def add_username_segment(powerline):
    import os
    if powerline.args.shell == 'bash':
        user_prompt = ' \xF0\x9F\x91\xA6  \\u '
    elif powerline.args.shell == 'zsh':
        user_prompt = ' %n '
    else:
        user_prompt = ' %s ' % os.getenv('USER')

    if os.getenv('USER') == 'root':
        bgcolor = Color.USERNAME_ROOT_BG
    else:
        bgcolor = Color.USERNAME_BG

    powerline.append(user_prompt, Color.USERNAME_FG, bgcolor)
