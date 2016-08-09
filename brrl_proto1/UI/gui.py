#-*- coding: utf-8 -*-
import libtcodpy as libtcod

# import gset
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import game_settings as gset


#offscreen
class Screen(object):
    '''
    렌더링의 최소단위인 RenderObject를 저장하고 렌더링하며 관리한다.
    libtcod.console을 wrapping한다.

    x,y 좌표는 루트콘솔을 기준으로 한다.
    스크린의 좌표가 달라지면 스크린에 포함된 모든 renderObject의 렌더링 위치(루트콘솔 기준)가 달라진다.
    '''
    def __init__(self, x, y, w, h, 
                 foreColor = libtcod.white, backColor = libtcod.black,
                 foreAlphaRatio = 1.0, backAlphaRatio = 0.0):
        self.console = libtcod.console_new(w,h)        
        self.foreColor = foreColor
        self.backColor = backColor        
        self.foreAlphaRatio = foreAlphaRatio
        self.backAlphaRatio = backAlphaRatio
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self._renderObjList = [] 
        libtcod.console_set_default_foreground(self.console, foreColor)
        libtcod.console_set_default_background(self.console, backColor)
        self.clear()

    def clear(self):
        ''' 
        Screen의 libtcod.console을 Screen의 초기값인
        foreground color와 background color로 초기화한다.
        '''
        libtcod.console_clear(self.console)        

    def renderAll(self):
        ''' 
        Screen에 포함된 모든 RenderObject들을 렌더링한다. 
        주의-화면을 표시(blit)하는 것은 아니다.
        '''
        self.clear()
        for renderObj in self._renderObjList:
            renderObj.render()

    def blit(self, renderX=0, renderY=0):
        '''
        Screen을 화면에 표시한다.
        최상위 루트콘솔에 이 Screen의 console을 출력한다.
        '''  
        libtcod.console_blit(self.console,
                             0,0, self.w,self.h,
                             gset.ROOT_CONSOLE, 
                             self.x + renderX ,self.y + renderY,
                             self.foreAlphaRatio, self.backAlphaRatio)

    def renderAndBlit(self, renderX=0, renderY=0):
        '''
        렌더링하고 루트콘솔에 블리트한다.
        '''
        self.renderAll()
        self.blit(renderX,renderY)

    def hasRenderObjAt(self, xInScr, yInScr):
        for robj in self._renderObjList:
            if robj.x == xInScr and robj.y == yInScr:
                return True
        return False

    def __getitem__(self, index):
        return self._renderObjList[index]

    def _append(self, renderObj):
        ''' 
        이 모듈 밖에서 쓰지 마시오.
        Screen에서 renderObj를 넣는 것은 허용되지 않음.
        renderObj가 가지는 Screen을 바꾸시오.
        '''
        self._renderObjList.append(renderObj)

    def _remove(self, renderObj):
        ''' 
        이 모듈 밖에서 쓰지 마시오.
        Screen에서 renderObj를 빼는 것은 허용되지 않음.
        renderObj가 가지는 Screen을 바꾸시오.
        '''
        self._renderObjList.remove(renderObj)    
   
class ScreenManager:    
    ''' 
    게임 내의 Screen들을 관리한다. 
    '''
    def __init__(self):        
        self._screenList = []

    def add(self, screen):        
        ''' 늦게 추가된 스크린이 전에 추가된 스크린을 가린다. '''
        self._screenList.append(screen)

    def blitAll(self):
        for screen in self._screenList:
            screen.blit()
        
    
    def __getitem__(self,index):
        return self._screenList[index]


'''--------------------------------------------------------------------------------------'''

class RenderObject(object):
    '''
    Screen에서 렌더링될 수 있는 최소단위의 객체이다.
    Screen에 소속된 경우에만 렌더링된다.
    Screen의 셀 하나를 차지한다.
    주인공, 몬스터, 등 셀 하나를 차지하는 객체를 Screen에서 표현할 수 있고
    폭발효과, 가스효과나 건물 등은 여러개의 RenderObject로 표현할 수 있다.
    '''
    def __init__(self, ownerScreen, name, char, x, y, 
                 foreColor=libtcod.white, backColor=libtcod.black,
                 visible = True):
        self._ownerScreen = ownerScreen 
        self.name = name
        self.char = char
        self.x = x
        self.y = y
        self.foreColor = foreColor
        self.backColor = backColor
        self.visible = visible

        #owner type check
        if type(ownerScreen) != Screen and ownerScreen is not None:
            raise TypeError('ownerScreen must be Screen type')
        
        #overlap renderObj check(append to owner)
        if ownerScreen != gset.ROOT_CONSOLE and ownerScreen is not None:
            for obj in self._ownerScreen._renderObjList:
                if x == obj.x and y == obj.y:
                    raise RenderObjOverlapException()
            self._ownerScreen._append(self) 
        
        #only one cell check
        if len(char) != 1:
            raise notOneCharError

    def render(self):
        '''         
        visible=true 보이는 상태이고
        Screen에 포함되어 있으면
        자신의 foreground color와 background color에 따라 
        Screen(의 콘솔에) char를 출력한다.
        '''
        if self.visible is True:
            if self.ownerScreen is not None:
                owner = self._ownerScreen
            
                prevBackFlag = libtcod.console_get_background_flag(owner.console)
                prevForeColor = owner.foreColor
                prevBackColor = owner.backColor
                #renderObj의 색깔로 설정
                libtcod.console_set_background_flag(owner.console, libtcod.BKGND_SET)
                libtcod.console_set_default_foreground(owner.console, self.foreColor)
                libtcod.console_set_default_background(owner.console, self.backColor)
                #출력
                libtcod.console_print(owner.console, self.x, self.y, self.char)
                #원래 owner의 색깔로 되돌리기.
                libtcod.console_set_background_flag(owner.console, prevBackFlag)
                libtcod.console_set_default_foreground(owner.console, prevForeColor)
                libtcod.console_set_default_background(owner.console, prevBackColor)
            else:
                raise NoOwnerRenderObjError()

    @property
    def ownerScreen(self):
        return self._ownerScreen
    
    @ownerScreen.setter
    def ownerScreen(self, screen):
        if self._ownerScreen is not None:
            self.ownerScreen._remove(self)
        if screen is not None:
            screen._append(self)
        self._ownerScreen = screen

'''--------------------------------------------------------------------------------------'''

class Font:
    ''' 
    외부에서 폰트를 로드할 때 사용된다. 
    '''
    def __init__(self, filePath, fontLayoutFlag, nbCharHoriz,nbCharVertic):
        self.filePath = filePath
        self.layoutFlag = fontLayoutFlag
        self.nbCharHoriz = nbCharHoriz
        self.nbCharVertic = nbCharVertic
        
'''-----------------------------------CustomExceptions------------------------------------'''

class notOneCharError(ValueError):
    def __str__(self):
        ''' RenderObject는 스크린에서 반드시 1개의 문자로 표시되어야 합니다. ''' 
        return "RenderObject must be expressed only one character on Screen."

class NoOwnerRenderObjError(RuntimeError):
    def __str__(self):
        ''' 스크린에 소속되지 않은 RenderObject는 렌더링할 수 없습니다. ''' 
        return "if RenderObject's owner is None, it can't render itself."

class RenderObjOverlapException(RuntimeError):
    def __str__(self):
        ''' 하나의 스크린에 1개를 초과하는 RenderObj가 한 타일(동일좌표)에 있을 수 없습니다. ''' 
        return "in a Screen, only one RenderObj can be located at one tile. "