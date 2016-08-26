#-*- coding: utf-8 -*-

import unittest
import libtcodpy as libtcod

# import gset
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import game_settings as gset

# import gui
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import gui


class Test_gui(unittest.TestCase):
    def setUp(self):
        #윈도우, 루트콘솔 셋팅
        defaultFont = gui.Font('font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        gset.setWindow(defaultFont, gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 'test window')
        gset.setLimitFps(gset.LIMIT_FPS)
             
        #screenManager, offscreen console 셋팅
        self.screenManager = gui.ScreenManager()
        self.screenManager.add(gui.Screen(10,10, 
                                          gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 
                                          backColor=libtcod.darkest_blue, backAlphaRatio=1.0))
        self.screenManager.add(gui.Screen(0,0, 
                                          10,10, 
                                          backColor=libtcod.red, backAlphaRatio=0.5))
            
    def test_GameLoop(self):
        ''' 이 함수에서 게임루프를 돌리면서 테스트를 한다. '''
        i = 0
        screen1 = self.screenManager[0]
        screen2 = self.screenManager[1]

        #3-1. char 1개 @ 
        renderObj = gui.RenderObject(screen1, '1','@', 0, 1)
        #3-2. char 1개 색깔다른 c  
        coloredRenderObj = gui.RenderObject(screen1, '2', u'너', 0, 20,
                                        libtcod.dark_gray, libtcod.yellow)
        #3-3. visible 테스트
        vFalseObj = gui.RenderObject(screen1, '3', 'v', 0, 3, visible=False)
        
        '''
        #TODO: 이 부분을 gameLoop로 캡슐화해야한다.
        #나중에 AI까지 만들었을 때 비로소 게임루프를 디자인할 수 있을 것이다.
        #일단은 냅두는게 나을 거 같다.
        '''
        while not libtcod.console_is_window_closed() :
            # ■■■버퍼 지우기■■■
            libtcod.console_clear(0) 

            #1.두 콘솔이 모두 제대로 출력되는가?
            libtcod.console_print(self.screenManager[0].console, 1, 2, u'제로 콘솔 테스트 ')
            libtcod.console_print(self.screenManager[1].console, 0, 0, u'오프 콘솔 테스트 ') 
            #self.screenManager.blitAll()
             
            #2.콘솔 이동
            self.consoleMove(i)
            i += 1

            #3.렌더링                        
            screen1.blit()
            screen2.blit()
            screen1.renderAll()            
            screen2.renderAll()

            '''
            #이런 순서로 하면 글자가 출력이 안됨. libtcod의 숨겨진 feature임.
            screen1.renderAll()            
            screen2.renderAll()
            screen1.blit()
            screen2.blit()
            '''

            #self.screenManager.blitAll()

            
            #4.RenderObject 이동
            renderObj.x += 1
            renderObj.y += 1

            #5.Screen 이동
            screen1.y -= 1
            
            # ■■■버퍼 비우기■■■
            libtcod.console_flush() 

            #다음 테스트로!
            if i == 15:
                break
    
    def test_createZeroCellRenderObj(self):    
        ''' RenderObject의 char가 ''이면 예외 발생  ''' 
        owner = self.screenManager[0]  
        self.assertRaises(gui.notOneCharError,
            lambda: gui.RenderObject(owner, 'user','', 3, 5))
            
    def test_createManyCellRenderObj(self):    
        ''' RenderObject의 char가 '1개이상'인 문자열이면 예외 발생 ''' 
        owner = self.screenManager[0]  
        self.assertRaises(gui.notOneCharError,
            lambda: gui.RenderObject(owner, 'user', u'1개이상', 3, 5))

    def test_ownerMustBeScreenType(self):
        ''' 루트콘솔은 들어갈 수 없다. RenderObject.owner는 Screen이지 console이 아니다. '''
        self.assertRaises(TypeError,
            lambda: gui.RenderObject(gset.ROOT_CONSOLE,'foo', '2',0,0))
            
    def test_noOwnerRenderObj(self):
        ''' ownerScreen을 None 으로 할 경우 렌더링 불가능. '''
        renderObj = gui.RenderObject(None, 'src', 's', 1,1)
        self.assertRaises(gui.NoOwnerRenderObjError, lambda: renderObj.render())

    
    #RenderObject.ownerScreen을 건드리면 반드시 그 스크린에 간섭해야한다 (초기화시에도)
    def test_addRenderObjToNewScreen(self):
        ''' 1.새 renderObj가 들어오는 Screen에 obj의 참조를 넣어준다. '''
        screen = gui.Screen(1,1,2,2)     
        renderObj = gui.RenderObject(screen, 'src', 's', 1,1)
        
        self.assertEqual(len(screen._renderObjList), 1, 'add 1 obj - broken:  0 --X--> 1')
        self.assertEqual(screen[0], renderObj, 'added and peek a renderObj')
        self.assertEqual(renderObj.ownerScreen, screen)
    '''
    def test_appendRenderObj(self):
        screen = gui.Screen(1,1,2,2)   
        renderObj = gui.RenderObject(None, 'src', 's', 1,1)

        screen.append(renderObj)
        self.assertEqual(renderObj.ownerScreen, screen)
    '''
    def test_removeRenderObjFromOldScreen(self):
        ''' 2. renderObj가 나가는 Screen의 저장소에서 obj의 참조를 제거한다. '''
        oldScreen = gui.Screen(0,0, 1,1)
        newScreen = gui.Screen(10,10, 1,1)
        
        renderObj = gui.RenderObject(oldScreen, 'src', 's', 1,1)
        self.assertEqual(len(oldScreen._renderObjList), 1, 'add 1 obj - broken: 0 --X--> 1')

        #change owner
        renderObj.ownerScreen = newScreen

        self.assertEqual(len(newScreen._renderObjList), 1, 'add 1 obj - broken: 0 --X--> 1')
        self.assertEqual(len(oldScreen._renderObjList), 0, 'remove 1 obj - broken: 1 --X--> 0')
        self.assertEqual(renderObj.ownerScreen, newScreen)

    def test_moveRenderObjFromScreenToNone(self):
        ''' 3. 어떤 Screen에 있던 renderObj를 제거한다(None으로) '''
        oldScreen = gui.Screen(0,0, 1,1)
        renderObj = gui.RenderObject(oldScreen, 'src', 's', 1,1)

        renderObj.ownerScreen = None
        self.assertEqual(len(oldScreen._renderObjList), 0, 'remove 1 obj - broken: 1 --X--> 0')

    def test_moveRenderObjFromNoneToScreen(self):
        ''' 4. None이 되있는 renderObj에서 Screen으로 이동 '''
        newScreen = gui.Screen(10,10, 1,1)
        renderObj = gui.RenderObject(None, 'src', 's', 1,1)

        #from None to Screen
        renderObj.ownerScreen = newScreen

        self.assertEqual(len(newScreen._renderObjList), 1, 'add 1 obj - broken: 0 --X--> 1')
        self.assertEqual(renderObj.ownerScreen, newScreen)
    
    def test_moveScreenAtoA(self):
        ''' 같은 스크린에서 같은 스크린으로 이동하는 경우는?(예외적)   걍 뻘짓임  '''
        screen = gui.Screen(1,1,2,2)     
        renderObj = gui.RenderObject(screen, 'src', 's', 1,1)
        renderObj.ownerScreen = screen
        self.assertEqual(len(screen._renderObjList), 1, 'is it changed??')   
                 
    def test_oneCellOneRenderObj(self):
        ''' 하나의 스크린 내에 위치가 겹치는 RenderObject는 있을 수 없다. '''
        screen = gui.Screen(1,1,2,2)
        obj1 = gui.RenderObject(screen, '1', '1', 1,1)       
        self.assertRaises(gui.RenderObjOverlapException,
            lambda: gui.RenderObject(screen, '2', '2', 1,1))        

    def test_screenHasRenderObjAtXY(self):
        x = 1
        y = 1
        screen = self.screenManager[0]
        renderObj = gui.RenderObject(screen, '1','@', x, y)        
        self.assertTrue(screen.hasRenderObjAt(x,y))
        self.assertEqual(screen.hasRenderObjAt(x+1,y+1), False)

    def consoleMove(self,time):
        if time == 5:
            #x값을 옮기면 이전 흔적이 지워지는가?
            self.screenManager[1].x = time   
        elif time == 10:
            #y값을 옮기면 이전 흔적이 지워지는가?
            self.screenManager[1].y = time   


if __name__ == '__main__':
    unittest.main()
