#-*- coding: utf-8 -*-
'''
결론:
key는 vk나 c만으로 체크할 수 없다.
둘 다 써야 한다.

문자로 표현할 수 없는 키들은 vk를 써야하고 
-> 특히 그런 키들은 c가 0이다.
(ex: F1, F2, Enter, 숫자패드와 그냥 숫자키)

문자로 표현할 수 있는 키들은 c를 써야 한다 
-> 문자로 표현 가능한 키들의 vk는 대부분 65이다.

'''
import unittest

import libtcodpy as libtcod

SCREEN_WIDTH = 30
SCREEN_HEIGHT = 30
LIMIT_FPS = 20

libtcod.console_set_custom_font( 'font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python + libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)

while not libtcod.console_is_window_closed():
    #이벤트를 받을 수 있는 환경을 구성한다.
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
    if key.vk != libtcod.KEY_NONE:
        print chr(key.c), ':', key.vk, key.c, ' | ' ,key.lalt, key.lctrl, key.ralt, key.rctrl, key.shift