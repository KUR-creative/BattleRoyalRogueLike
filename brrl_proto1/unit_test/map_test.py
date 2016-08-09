#-*- coding: utf-8 -*-

import unittest
import libtcodpy as libtcod



# import gset
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import game_settings as gset

#import Map
from brrl_proto1 import Map

# import gui
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import gui


class Test_map(unittest.TestCase):
    def setUp(self):
        self.map = Map.Map() #매 setUp마다 갈아치우기 때문에 tearDown은 노필요.

        self.scr1 = gui.Screen(30,30, 10,10, backColor=libtcod.darkest_red, backAlphaRatio=1.0)
        self.scr2 = gui.Screen(35,35, 10,10, backColor=libtcod.darkest_blue, backAlphaRatio=1.0)
        
        self.map.add(self.scr1)
        self.map.add(self.scr2)

        return super(Test_map, self).setUp()
    
    def test_mapHasScreens(self):                
        self.assertEqual(self.map[0], self.scr1, "map can't have Screen")
        self.assertEqual(self.map[1], self.scr2, "map can't have Screen")
        self.assertEqual(len(self.map._screenList), 2, 'need tearDown')

    def test_renderScreensInMap(self):
        #윈도우, 루트콘솔 셋팅
        defaultFont = gui.Font('font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        gset.setWindow(defaultFont, gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 'test window')
        gset.setLimitFps(gset.LIMIT_FPS)

        libtcod.console_print(self.scr1.console, 0,0, 'scr1')
        libtcod.console_print(self.scr2.console, 0,0, 'scr2')

        i = 0
        while not libtcod.console_is_window_closed():
            # ■■■버퍼 지우기■■■
            libtcod.console_clear(0) 

            #맵에 있는 스크린들 모두 그리기
            #빨리 넣은 것이 바닥에 있어야 한다.
            self.map.blitAll()

            #움직이기 렌더링 테스트
            self.map.x -= 1
            self.map.y -= 1

            # ■■■버퍼 비우기■■■
            libtcod.console_flush() 
            
            #다음 테스트로!
            i += 1
            if i == 20:
                break

if __name__ == '__main__':
    unittest.main()
