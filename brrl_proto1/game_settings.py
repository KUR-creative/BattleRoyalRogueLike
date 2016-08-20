#-*- coding: utf-8 -*-
import libtcodpy as libtcod

WINDOW_WIDTH = 50
WINDOW_HEIGHT = 40
LIMIT_FPS = 60 # 이게 너무 작으면 입력이 지연되는 것처럼 보일 수 있다.
ROOT_CONSOLE = 0 #root console(NULL)

def setWindow(font, w, h, title, isFullScreen = False):    
    libtcod.console_set_custom_font( font.filePath, font.layoutFlag, font.nbCharHoriz, font.nbCharVertic)
    libtcod.console_init_root(w, h, title, isFullScreen)

def setLimitFps(limitFps):
    libtcod.sys_set_fps(limitFps)

