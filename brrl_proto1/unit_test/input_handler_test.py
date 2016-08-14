#-*- coding: utf-8 -*-
import unittest
import libtcodpy as libtcod

# import input_handler
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import input_handler as ihdr


testInputDict ={ihdr.KeyTuple(ihdr.NOT_VK,'c') : 'in a dict',
                ihdr.KeyTuple(ihdr.NOT_VK,'c', lalt=True) : 'c + lalt',
                ihdr.KeyTuple(ihdr.NOT_VK,'a') : 'input a, s, d key',
                ihdr.KeyTuple(ihdr.NOT_VK,'s') : 'input a, s, d key',
                ihdr.KeyTuple(ihdr.NOT_VK,'d') : 'input a, s, d key',
                ihdr.KeyTuple(libtcod.KEY_F1, ihdr.NOT_CHAR) : 'input F1, esc',
                ihdr.KeyTuple(libtcod.KEY_ESCAPE, '\x1b') : 'input F1, esc',
                ihdr.KeyTuple(libtcod.KEY_ALT, ihdr.NOT_CHAR, lalt=True) : 'only lalt'}

class Test_inputHandler(unittest.TestCase):
    def setUp(self):
        self.key = libtcod.Key()                
        self.ihandler = ihdr.InputHandler(self.key, testInputDict)

    def test_keyInput_char(self):
        #key에 char가 들어온 상황을 모사한다.

        #given: 사용자가 'a' 입력        
        #when: 루프 중에 입력모듈이 입력 캐치

        #vk는 따로 설정해준다.
        self.key.vk = 65
        ret = self.inputChar('a')
        #then:
        self.assertEqual(ret, 'input a, s, d key')
        
        ret = self.inputChar('s')
        self.assertEqual(ret, 'input a, s, d key')

        ret = self.inputChar('d')
        self.assertEqual(ret, 'input a, s, d key')

        ret = self.inputChar('x')
        self.assertNotEqual(ret, 'input a, s, d key')

    def test_keyInput_vk(self):
        #when: 사용자가 'F1' 입력     
        self.key.vk = libtcod.KEY_F1
        self.key.c = 0
        self.assertEqual(self.ihandler.getSemanticInput(), 'input F1, esc')
            
        self.key.vk = libtcod.KEY_ESCAPE
        self.key.c = ord('\x1b')
        self.assertEqual(self.ihandler.getSemanticInput(), 'input F1, esc')

        self.key.vk = 65
        self.key.c = 0
        self.assertIsNone(self.ihandler.getSemanticInput())

    def test_InputTableSetup(self):
        key = self.key
        #inputDict에 있는 char가 입력됨        
        key.vk = 65 
        key.c = ord('c')
        self.assertEqual(self.ihandler.getSemanticInput(), 'in a dict')

        #inputDict에 없는 char가 입력됨
        ret = self.inputChar('x')
        self.assertIsNone(ret)

        #inputDict에 있는 F1(vk)가 입력됨
        key.vk = libtcod.KEY_F1
        key.c = 0
        self.assertEqual(self.ihandler.getSemanticInput(), 'input F1, esc')
                
        #inputDict에 없는 vk가 입력됨
        key.vk = libtcod.KEY_F2
        key.c = 0
        self.assertIsNone(self.ihandler.getSemanticInput())

        #lalt 같이 누르기
        key.vk = 65 #이게 65가 아닐 수 있다!
        key.c = ord('c')
        key.lalt = True
        self.assertEqual(self.ihandler.getSemanticInput(), 'c + lalt')

        #lalt만 누르기
        key.vk = 7
        key.c = 0
        key.lalt = True; key.lctrl = False
        key.ralt = False; key.rctrl = False
        key.shift  = False
        self.assertEqual(self.ihandler.getSemanticInput(), 'only lalt')

    def test_sameInputButDifferentOutput(self):
        self.fail("test for InputResult class.. for what? maybe need to delete this test")

    
    def test_inputModuleInGameLoop(self):
        libtcod.console_set_custom_font( 'font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        libtcod.console_init_root(30, 30, 'python + libtcod tutorial', False)
        libtcod.sys_set_fps(20)

        #이벤트를 받을 수 있는 환경을 구성한다.
        mouse = libtcod.Mouse()
        key = libtcod.Key()
        self.ihandler.key = key

        print "let's manual test! press esc to cancel"
        i = 0
        while not libtcod.console_is_window_closed():                      
            libtcod.console_flush()  
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
            str = self.ihandler.getSemanticInput()            
            if key.vk != libtcod.KEY_NONE:
                print str
            if key.vk == libtcod.KEY_ESCAPE:
                break
            if i == 10:
                break
            i += 1

    

    def inputChar(self, char):
        self.key.c = ord(char)
        return self.ihandler.getSemanticInput()


if __name__ == '__main__':
    unittest.main()
    