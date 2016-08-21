#-*- coding: utf-8 -*-
import unittest

import libtcodpy as libtcod

# import from sibling package
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import gui
from UI import input_handler as ihdr

# import from root package
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import game_settings as gset
from brrl_proto1 import Map
from brrl_proto1 import GameObjectFactory as gfac
from brrl_proto1 import GameObjectRepository as grepo

import game_state_changer_test1 as gsch

'''
#유틸리티
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

userSemantics = enum('UP', 'DOWN', 'LEFT', 'RIGHT', 'SKIP', 'EXIT')  
'''



#### make functions ####
def createTile(x,y):     
    tile = gui.RenderObject(terrainScreen,
                            'tile'+ str(x+y), str(x+y)[-1],
                            x,y, backColor=libtcod.white)
    return gsch.GameObject(x,y, tile)

def createTree(num):
    tree = gui.RenderObject(mapObjScreen,
                            'tree'+ str(num), u'●',
                            num*2,num*2, foreColor=libtcod.darkest_red)
    obsCompo = gsch.Obstacle(True)
    return gsch.GameObject(num*2, num*2, tree, obsCompo)

def createEnemy(x,y):
    #이렇게 체크를 꼭 해서 겹치는 obstacle이 있으면 안 된다..
    if isObstacleAt(x,y):
        x += 1
    rCompo = gui.RenderObject(npcScreen,'enemy',u'적', 
                                  x,y,
                                  foreColor=libtcod.blue)
    obsCompo = gsch.Obstacle(True)
    fCompo = gsch.Fighter(30)
    tCompo = gsch.TurnTaker(2)
    return gsch.GameObject(x, y, 
                           renderComponent=rCompo, 
                           obstacleComponent=obsCompo,
                           fighterComponent=fCompo,
                           turnTakerComponent=tCompo,
                           stateChangerComponent=proto1StateChangerCompo())

def createUserPlayer():       
    initX = 4
    initY = gset.WINDOW_HEIGHT/2
    rCompo = gui.RenderObject(userScreen,'user',u'나', 
                              initX,initY,
                              foreColor=libtcod.black)
    obsCompo = gsch.Obstacle(True)
    fCompo = gsch.Fighter(100)
    tCompo = gsch.TurnTaker(1)
    return gsch.GameObject(initX, initY, 
                           renderComponent=rCompo, 
                           fighterComponent=fCompo,
                           turnTakerComponent=tCompo,
                           stateChangerComponent=proto1StateChangerCompo())


######## 100% 게임로직 됨 game logic(game specific) ########

class proto1StateChangerCompo:
    '''
    이번 프로토타입의 유저만을 위한 상태 변경클래스이다.
    맨날 겹치는 부분은 상속을 해도 되겠다.

    매우 자주 변하는 부분이겠다.
    그러니까 코드가 좀 더러워도 되나?
    
    TODO: refactoring 외부 참조(특히 isobstacle)같은 거는 없는게 좋다.
    이 클래스의 생성자에 받아 가라.

    'up' 같은 걸 enum으로 만들거나 아예 owner에서 함수를 줘서 호출할수도 있다.
    1.enum을 쓰는 방법은 여기서 적당히 상태변화의 책임을 진다.
        이 클래스 자체의 의미가 상태변화의 책임을 지는 것이니까... 이게 맞아.
    2.함수를 줘서 호출하는 건 gameObject에 상태변화의 모든 책임을 넘기는 것이다.
        ㄴ 이 방법은 아무래도 제약이 많을 거 같다... 역시...

    그런데, stateChangerComponent가 모든 플레이어에게 동일해도 괜찮다면, 
    그냥 stateChanger에서 상태를 변경할 수도 있다.

    근데 아직 잘 모르겠다. 잘 모르는 것에 대해서는 덜 유연한 디자인 결정을 내려선 안 된다.
    '''

    '''
    #enum 살려내라 으아아!
    def changeState(self, semanticInput):
        print semanticInput, ' ', #DBG

        if semanticInput is None:
            return None        
        
        if semanticInput == userSemantics.UP:
            self.moveOwner(0, -1)
        elif semanticInput == userSemantics.DOWN:
            self.moveOwner(0, +1)
        elif semanticInput == userSemantics.LEFT:
            self.moveOwner(-1, 0)
        elif semanticInput == userSemantics.RIGHT:
            self.moveOwner(+1, 0)

        if semanticInput == userSemantics.EXIT:
            return semanticInput 
    '''
    def changeState(self, semanticInput):
        print semanticInput, ' ', #DBG

        if semanticInput is None:
            return None        
        
        if semanticInput == 'up':
            self.moveOwner(0, -1)
        elif semanticInput == 'down':
            self.moveOwner(0, +1)
        elif semanticInput == 'left':
            self.moveOwner(-1, 0)
        elif semanticInput == 'right':
            self.moveOwner(+1, 0)

        if semanticInput == 'skip':
            self.owner.skip()

        if semanticInput == 'exit':
            return semanticInput 
    

    def moveOwner(self, dx, dy):
        if isObstacleAt(self.owner.x + dx, self.owner.y + dy):
            print "cannot move over blocked obstacle!"  
        else:
            self.owner.move(dx, dy)
            

'''
inputTable = {ihdr.KeyTuple(libtcod.KEY_ESCAPE, '\x1b'):      userSemantics.EXIT,
              ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):   userSemantics.UP,
              ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): userSemantics.DOWN,
              ihdr.KeyTuple(libtcod.KEY_LEFT, ihdr.NOT_CHAR): userSemantics.LEFT,
              ihdr.KeyTuple(libtcod.KEY_RIGHT, ihdr.NOT_CHAR):userSemantics.RIGHT} 
'''
inputTable = {ihdr.KeyTuple(libtcod.KEY_ESCAPE, '\x1b'):      'exit',
              ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):   'up',
              ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): 'down',
              ihdr.KeyTuple(libtcod.KEY_LEFT, ihdr.NOT_CHAR): 'left',
              ihdr.KeyTuple(libtcod.KEY_RIGHT, ihdr.NOT_CHAR):'right'} 

class proto1OnlyUpAi(object):
    def calcNextAct(self, nowGameState):
        return 'up'
class proto1OnlyDownAi(object):
    def calcNextAct(self, nowGameState):
        return 'down'
class proto1OnlySkipAi(object):
    def calcNextAct(self, nowGameState):
        return 'skip'

################################

def isObstacleAt(xInMap, yInMap):
    '''
    입력된 좌표에서 장애물이 있는가?

    :param int xInMap: 알고 싶은 맵의 x좌표
    :param int yInMap: 알고 싶은 맵의 y좌표
    :returns: Obstacle이 있으면 True / 없으면 False
    '''
    for obstacleRef in obstacleObjRefs:
        if(obstacleRef().x == xInMap and 
           obstacleRef().y == yInMap):
            return True
    return False

#### 약한 참조 저장소 ####
#지형 저장소
tileRefs = [[None
                for y in range(gset.WINDOW_HEIGHT)]
                for x in range(gset.WINDOW_WIDTH)]
#막아서는 놈들 저장소: 반드시 여기에 저장되는게 보장되어야 한다.(버그가 없으려면)
obstacleObjRefs = []
#진짜 적
enemyRefs = []
#유저
userRef = None


class Test_prototype1(unittest.TestCase):
    def test_prototype1(self):
        #창 초기화
        font = gui.Font('font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        gset.setWindow(font, gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 'test')
        gset.setLimitFps(gset.LIMIT_FPS)

        #맵에 스크린 배치(TODO: 전역객체를 없애는게 좋지 않을까?)
        global terrainScreen, mapObjScreen, npcScreen, userScreen

        self.map = Map.Map()
        terrainScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT, backAlphaRatio=1.0)
        mapObjScreen =  gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        npcScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        userScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        self.map.add(terrainScreen)
        self.map.add(mapObjScreen)
        self.map.add(npcScreen)
        
        #게임 오브젝트 생성 준비
        global gameObjFactory
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
                        
        #3.~ 지형 생성
        for x in range(gset.WINDOW_WIDTH):
            for y in range(gset.WINDOW_HEIGHT):
                tileRefs[x][y] = gameObjFactory.createGameObject(lambda:createTile(x,y))
        #3.~ 맵 구성요소 생성 
        for i in range(13): 
            obstacleObjRefs.append( gameObjFactory.createGameObject(lambda:createTree(i)) )
        '''
        #3.~ 더미 적 생성
        dummyRef = gameObjFactory.createGameObject(createDummyEnemy)
        obstacleObjRefs.append(dummyRef)
        '''
        #3.~ 진짜 적 생성
        for i in range(4):
            enemyRef = gameObjFactory.createGameObject(lambda:createEnemy(i*10, i*5))
            obstacleObjRefs.append(enemyRef)
            enemyRefs.append(enemyRef)
        
        #3.~ 유저 생성
        global userRef 
        userRef = gameObjFactory.createGameObject(createUserPlayer)
        obstacleObjRefs.append(userRef)

        user = userRef()
        
        #입력 준비        
        self.key = libtcod.Key()
        
        #유저와 인공지능과 플레이어(gobj)들
        playerList = [user, enemyRefs[0](), enemyRefs[1](), enemyRefs[2](), enemyRefs[3](),]                      
        userList = [ihdr.InputHandler(self.key, inputTable),
                    gsch.AiInputHandler(playerList[0], proto1OnlyDownAi()),
                    gsch.AiInputHandler(playerList[1], proto1OnlyUpAi()),
                    gsch.AiInputHandler(playerList[2], proto1OnlySkipAi()),
                    gsch.AiInputHandler(playerList[3], proto1OnlyDownAi())]        
                        
        turnSystem = gsch.TurnSystem(userList, playerList)

        #게임 루프
        while not libtcod.console_is_window_closed():
            #턴 시스템 작동.
            exit = turnSystem.run()

            if exit == 'exit':
                break

            # 렌더링
            # ■■■버퍼 지우기■■■
            libtcod.console_clear(0) 
            self.map.renderAndBlit()
            userScreen.renderAndBlit()            
            # ■■■버퍼 비우기■■■
            libtcod.console_flush() 
     

if __name__ == '__main__':
    unittest.main()
