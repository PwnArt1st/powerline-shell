#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import re
import sys
reload(sys) # ugly hack to access sys.setdefaultencoding
sys.setdefaultencoding('utf-8')

py3 = sys.version_info.major == 3


def warn(msg):
    print('[powerline-bash] ', msg)


class Powerline:
    symbols = {
        'compatible': {
            'lock': 'RO',
            'network': 'SSH',
            'separator': u'\u25B6',
            'separator_right': u'\uE0B2',
            'separator_thin': u'\u276F'
        },
        'patched': {
            'lock': u'\uE0A2',
            'network': u'\uE0A2',
            'separator': u'\uE0B0',
            'separator_thin': u'\uE0B1',
            'separator_right': u'\uE0B2',
            'separator_right_thin': u'\uE0B3',
        },
        'flat': {
            'lock': '',
            'network': '',
            'separator': '',
            'separator_thin': ''
        },
    }

    color_templates = {
        'bash': '\\[\\e%s\\]',
        'zsh': '%%{%s%%}',
        'bare': '%s',
    }

    def __init__(self, args, cwd, side, width=0):
        self.args = args
        self.cwd = cwd
        mode, shell = args.mode, args.shell
        self.color_template = self.color_templates[shell]
        self.reset = self.color_template % '[0m'
        self.lock = Powerline.symbols[mode]['lock']
        self.network = Powerline.symbols[mode]['network']
        self.separator = Powerline.symbols[mode]['separator']
        self.separator_thin = Powerline.symbols[mode]['separator_thin']
        self.separator_right = Powerline.symbols[mode]['separator_right']
        self.segments = []
        self.segments_right = []
        self.segments_down = []
        self.width=width
        self.mode='left'
        self.side=side

    def color(self, prefix, code):
        if code is None:
            return ''
        else:
            return self.color_template % ('[%s;5;%sm' % (prefix, code))

    def fgcolor(self, code):
        return self.color('38', code)

    def bgcolor(self, code):
        return self.color('48', code)

    def append(self, content, fg, bg, separator=None, separator_fg=None):
        segment=(content, fg, bg,
            separator if separator is not None else self.separator,
            separator_fg if separator_fg is not None else bg)
        
        if self.mode == 'right':
            self.segments_right.append(segment)
        elif self.mode == 'down':
            self.segments_down.append(segment)
        else:
            self.segments.append(segment)

    def appendMode(self, mode='left'):
        self.mode = mode
    
    def draw(self):
        leftSegmentsText = [self.draw_segment(idx) for idx in range(len(self.segments))]
        rightSegmentsText = [self.draw_segment(idx, "right") for idx in range(len(self.segments_right))]
        downSegmentsText = [self.draw_segment(idx, "down") for idx in range(len(self.segments_down))]
        
        leftText  = u''.join(leftSegmentsText)  + self.reset + ' '
        rightText = u''.join(rightSegmentsText) + self.reset
        downText  = u''.join(downSegmentsText)  + self.reset + ' '
        
        leftRawText  = u''.join([segment[0] + self.separator for segment in self.segments]) + self.reset + ' '
        rightRawText = u''.join([segment[0] + self.separator for segment in self.segments_right]) + self.reset + ' '
        
        leftWidth = len(leftRawText.encode("ascii","replace"))
        rightWidth = len(rightRawText.encode("ascii","replace"))
        spaces = ' ' * (self.width - leftWidth - rightWidth)
        
        if self.side == 'both':
            line = leftText + spaces + rightText + "\n" + downText
        elif self.side == 'right':
            line = rightText
        else: #left
            line = leftText + "\n" + downText
        
        return line
        
    def segment_length(self, idx, source=None):
        if source == "right":
            segment = self.segments_right[idx]
            next_segment = self.segments_right[idx - 1] if idx > 0 else None
        elif source == "down":
            segment = self.segments_down[idx]
            next_segment = self.segments_down[idx + 1] if idx < len(self.segments_down)-1 else None
        else:
            segment = self.segments[idx]
            next_segment = self.segments[idx + 1] if idx < len(self.segments)-1 else None

        return len(segment[0]) + len(segment[3])

    def draw_segment(self, idx, source=None):
        if source == "right":
            segment = self.segments_right[idx]
            next_segment = self.segments_right[idx - 1] if idx > 0 else None
        elif source == "down":
            segment = self.segments_down[idx]
            next_segment = self.segments_down[idx + 1] if idx < len(self.segments_down)-1 else None
        else:
            segment = self.segments[idx]
            next_segment = self.segments[idx + 1] if idx < len(self.segments)-1 else None
        
        if source == "right":
            return ''.join((
                self.bgcolor(next_segment[2]) if next_segment else self.reset,
                self.fgcolor(segment[4]) if next_segment else self.fgcolor(segment[2]),
                self.separator_right,
                
                self.fgcolor(segment[1]),
                self.bgcolor(segment[2]),
                segment[0]))
        else:
            return ''.join((
                self.fgcolor(segment[1]),
                self.bgcolor(segment[2]),
                segment[0],
                
                self.bgcolor(next_segment[2]) if next_segment else self.reset,
                self.fgcolor(segment[4]) if next_segment else self.fgcolor(segment[2]),
                self.separator))

def get_valid_cwd():
    """ We check if the current working directory is valid or not. Typically
        happens when you checkout a different branch on git that doesn't have
        this directory.
        We return the original cwd because the shell still considers that to be
        the working directory, so returning our guess will confuse people
    """
    # Prefer the PWD environment variable. Python's os.getcwd function follows
    # symbolic links, which is undesirable. But if PWD is not set then fall
    # back to this func
    try:
        cwd = os.getenv('PWD') or os.getcwd()
    except:
        warn("Your current directory is invalid. If you open a ticket at " +
            "https://github.com/milkbikis/powerline-shell/issues/new " +
            "we would love to help fix the issue.")
        sys.stdout.write("> ")
        sys.exit(1)

    parts = cwd.split(os.sep)
    up = cwd
    while parts and not os.path.exists(up):
        parts.pop()
        up = os.sep.join(parts)
    if cwd != up:
        warn("Your current directory is invalid. Lowest valid directory: "
            + up)
    return cwd


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--cwd-mode', action='store',
            help='How to display the current directory', default='fancy',
            choices=['fancy', 'plain', 'dironly'])
    arg_parser.add_argument('--cwd-only', action='store_true',
            help='Deprecated. Use --cwd-mode=dironly')
    arg_parser.add_argument('--cwd-max-depth', action='store', type=int,
            default=5, help='Maximum number of directories to show in path')
    arg_parser.add_argument('--cwd-max-dir-size', action='store', type=int,
            help='Maximum number of letters displayed for each directory in the path')
    arg_parser.add_argument('--colorize-hostname', action='store_true',
            help='Colorize the hostname based on a hash of itself.')
    arg_parser.add_argument('--mode', action='store', default='patched',
            help='The characters used to make separators between segments',
            choices=['patched', 'compatible', 'flat'])
    arg_parser.add_argument('--shell', action='store', default='bash',
            help='Set this to your shell type', choices=['bash', 'zsh', 'bare'])
    arg_parser.add_argument('--width', action='store', type=int,
            default=0, help='Width of the screen')
    arg_parser.add_argument('prev_error', nargs='?', type=int, default=0,
            help='Error code returned by the last command')
    arg_parser.add_argument('--side', action='store', default='both',
            help='What side to display.', choices=['both', 'left', 'right'])
    args = arg_parser.parse_args()

    powerline = Powerline(args, get_valid_cwd(), args.side, args.width)
