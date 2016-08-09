#-*- coding: utf-8 -*-

import unittest
import libtcodpy as libtcod

# import gui
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import gui

# import gset
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import game_settings as gset
from brrl_proto1 import Map


#1. 입력 준비
mouse = libtcod.Mouse()
key = libtcod.Key()

class Test_proto0(unittest.TestCase):
    def test_proto0(self):
        ''' 
        일단 만들어보면서 내가 만든 것을 더 알아간다. 
        proto0 완성!
        '''        

        #3. 렌더링 준비
        font = gui.Font('font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        gset.setWindow(font, gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 'test')
        gset.setLimitFps(gset.LIMIT_FPS)

        map = Map.Map()
        mapScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT, backColor=libtcod.darkest_blue, backAlphaRatio=1.0)
        map.add(mapScreen)
        
        userScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT, backAlphaRatio=0.0)
        user = gui.RenderObject(userScreen,'user',u'나', 
                                gset.WINDOW_WIDTH/2,gset.WINDOW_HEIGHT/2,
                                foreColor=libtcod.red)

        #맵도 꾸며보기.
        tiles = [[None
                  for y in range(gset.WINDOW_HEIGHT)]
                    for x in range(gset.WINDOW_WIDTH)]
        #위처럼 반대로 써놔야 tiles[50][40]
        #tiles[gset.WINDOW_WIDTH][gset.WINDOW_HEIGHT] 이렇게 된다.

        for x in range(gset.WINDOW_WIDTH):
            for y in range(gset.WINDOW_HEIGHT):
                if x == 25 and y == 19:
                    tiles[x][y] = gui.RenderObject(mapScreen,
                                                   'tile'+ str(x+y), str(x+y)[-1],
                                                   x,y, backColor=libtcod.green)
                else:
                    tiles[x][y] = gui.RenderObject(mapScreen,
                                                   'tile'+ str(x+y), str(x+y)[-1],
                                                   x,y, backColor=libtcod.gray)
        i = 0
        while not libtcod.console_is_window_closed():
            #1. 사용자 입력
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)

            #2. 게임 상태 변경
            if key.vk == libtcod.KEY_UP:
                map.y += 1 
            elif key.vk == libtcod.KEY_DOWN:
                map.y -= 1 
            elif key.vk == libtcod.KEY_LEFT:
                map.x += 1 
            elif key.vk == libtcod.KEY_RIGHT:
                map.x -= 1

            #3. 렌더링
            # ■■■버퍼 지우기■■■
            libtcod.console_clear(0) 

            map.renderAndBlit()
            userScreen.renderAndBlit()
            
            # ■■■버퍼 비우기■■■
            libtcod.console_flush() 

            i += 1
            if i == 10:
                break


if __name__ == '__main__':
    unittest.main()