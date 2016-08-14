#-*- coding: utf-8 -*-
import unittest
import libtcodpy as libtcod

# import gui
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import gui
# import input_handler
from UI import input_handler as ihdr

# import from root package
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import game_settings as gset
from brrl_proto1 import Map
from brrl_proto1 import GameObjectFactory as gfac
from brrl_proto1 import GameObjectRepository as grepo


################################## game logic ##################################
#(game specific)
'''
게임오브젝트는 반드시 약한 참조로 다뤄라.
직접 참조하면 안된다.

아직 잘 해봐야 프로토타입1이다. 게임 로직과 게임 셋팅이 강하게 결합되어 있다.
메이크함수 같은거 보면 알 수 있다.

게임 데이터를 쪼개서 재사용할 수 있게한다.

'''

#### 게임오브젝트와 컴포넌트 정의 ####
class Obstacle:
    def __init__(self, blocked=False):      
        self.blocked = blocked
        #fov 추가될 예정.

class Fighter(object):
    def __init__(self, hp, hpRegen, power, accuracy, defense):
        self._hp = hp
        self.hpRegen = hpRegen
        self.power = power
        self.accuracy = accuracy
        self.defense = defense

    def attack(self, targetRef):
        if targetRef is None:
            print "attack but no target!"
        else:
            target = targetRef()              
            damage = self.power - target.fighterComponent.defense
            coin = libtcod.random_get_int(0,1,100)
            if target.fighterComponent.hp > 0:
                if coin < self.accuracy:                
                    target.fighterComponent.hp -= damage
                    print ("Bonk!: your attack:", self.power, 
                           "but damage:", damage, 
                           "enemy hp:", target.fighterComponent.hp)
                else:
                    print "miss!"

    def die(self):
        #시체는 장애물이 아니다
        self.owner.obstacleComponent.blocked = False
        #시체 묘사
        self.owner.renderComponent.char = u'死' #이거 '%' 왜  출력 못하나?? 폰트에 없나?
        self.owner.renderComponent.foreColor = libtcod.red

        print self.owner.renderComponent.name + " is dead!"

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, val):
        self._hp = val
        if self._hp < 0:
            self.die()

class TurnTaker(object):
    def __init__(self, maxActCount, inputSource):
        self.maxActCount = maxActCount
        self.inputSource = inputSource
        self.actCount = maxActCount

    def takeTurn(self):
        self.actCount = self.maxActCount
        
        while self.actCount > 0:                
            result = self.inputSource.inputResult()
            if result is not None:
                actCost = result(self.owner)
                self.actCount -= actCost
            else:
                print "idle input",               
                        
class GameObject:
    def __init__(self, xInMap, yInMap, 
                 renderComponent=None, 
                 obstacleComponent=None, 
                 fighterComponent=None,
                 turnTakerComponent=None):
        self.x = xInMap
        self.y = yInMap
        
        self.renderComponent = renderComponent
        if renderComponent is not None:
            self.renderComponent.owner = self

        self.obstacleComponent = obstacleComponent
        if obstacleComponent is not None:
            self.obstacleComponent.owner = self

        self.fighterComponent = fighterComponent
        if fighterComponent is not None:
            self.fighterComponent.owner = self

        self.turnTakerComponent = turnTakerComponent
        if turnTakerComponent is not None:
            self.turnTakerComponent.owner = self
    
    def moveInMap(self, x, y, obstacleRefs):
        #print 'b:',self.x, self.y, ' ',
        
        canGo = True
        obstacle = None
        for objRef in obstacleRefs:            
            if((objRef().x == self.x + x and objRef().y == self.y + y)
                and objRef().obstacleComponent.blocked):
                    canGo = False
                    obstacle = objRef
        if canGo:
            self.x += x
            self.y += y
            #self.renderComponent.x = self.x
            #self.renderComponent.y = self.yInMap
            #print 'f:',self.x, self.yInMap, ' '            
        else:
            print "cannot move over blocked obstacle!"  
                 
        return obstacle

    def takeTurn(self, obstacleRefs):
        dx = libtcod.random_get_int(0, -1, 1)
        dy = libtcod.random_get_int(0, -1, 1)
        self.moveInMap(dx, dy, obstacleRefs)

    def move(self, dx, dy):
        if isObstacleAt(self.x + dx, self.y + dy):
            print "cannot move over blocked obstacle!"  
        else:
            self.x += dx
            self.y += dy

#### 약한 참조 저장소 ####
#지형 저장소
tileRefs = [[None
                for y in range(gset.WINDOW_HEIGHT)]
                for x in range(gset.WINDOW_WIDTH)]
#막아서는 놈들 저장소: 반드시 여기에 저장되는게 보장되어야 한다.(버그가 없으려면)
obstacleObjRefs = []
#더미 적
dummyRef = None
#진짜 적
enemyRefs = []
#유저
userRef = None

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


#### make functions ####
def createTile(x,y):     
    tile = gui.RenderObject(terrainScreen,
                            'tile'+ str(x+y), str(x+y)[-1],
                            x,y, backColor=libtcod.white)
    return GameObject(x,y, tile)

def createTree(num):
    tree = gui.RenderObject(mapObjScreen,
                            'tree'+ str(num), u'●',
                            num*2,num*2, foreColor=libtcod.darkest_red)
    mCompo = Obstacle(True)
    return GameObject(num*2, num*2, tree,mCompo)

def createDummyEnemy():
    initX = gset.WINDOW_WIDTH/2 - 5
    initY = gset.WINDOW_HEIGHT/2 - 5
    dummyActor = gui.RenderObject(npcScreen,'dummy',u'덤', 
                                initX,initY,
                                foreColor=libtcod.blue)
    mapCompo = Obstacle(True)
    fighter = Fighter(30, 10, 10, 50, 1)
    return GameObject(initX, initY, dummyActor, mapCompo, fighter)

def createEnemy():    
    initX = libtcod.random_get_int(0, 0, npcScreen.w)
    initY = libtcod.random_get_int(0, 0, npcScreen.h)
    while(npcScreen.hasRenderObjAt(initX, initY) or #스크린에 겹치는 애가 있거나
          isObstacleAt(initX, initY)):              #Obstacle이 겹치는 애가 있거나
        initX = libtcod.random_get_int(0, 0, npcScreen.w)
        initY = libtcod.random_get_int(0, 0, npcScreen.h)

    renderCompo = gui.RenderObject(npcScreen,'dummy',u'적', 
                                   initX,initY,
                                   foreColor=libtcod.flame)
    mapCompo = Obstacle(True)
    fighter = Fighter(30, 10, 10, 50, 1)
    return GameObject(initX, initY, renderCompo, mapCompo, fighter)
    
def createUserPlayer():       
    initX = gset.WINDOW_WIDTH/2
    initY = gset.WINDOW_HEIGHT/2
    renderComponent = gui.RenderObject(userScreen,'user',u'나', 
                                initX,initY,
                                foreColor=libtcod.black)
    fighter = Fighter(100, 10, 5, 80, 0)
    return GameObject(initX, initY, renderComponent, fighterComponent=fighter)

#### inputTable output functions (game state change functions) ####
def userMoveUp():
    user = userRef()
    obstacleRef = user.moveInMap(0,-1, obstacleObjRefs) 
    if obstacleRef is None:
        map.y += 1    
    else:
        if obstacleRef().fighterComponent is not None:
            user.fighterComponent.attack(obstacleRef)
        else:
            print "but didn't try to break this shit!"

def userMoveDown():
    user = userRef()
    obstacleRef = user.moveInMap(0,1, obstacleObjRefs) 
    if obstacleRef is None:
        map.y -= 1    
    else:
        if obstacleRef().fighterComponent is not None:
            user.fighterComponent.attack(obstacleRef)
        else:
            print "but didn't try to break this shit!"

def userMoveLeft():
    user = userRef()
    obstacleRef = user.moveInMap(-1,0, obstacleObjRefs) 
    if obstacleRef is None:
        map.x += 1  
    else:
        if obstacleRef().fighterComponent is not None:
            user.fighterComponent.attack(obstacleRef)
        else:
            print "but didn't try to break this shit!"

def userMoveRight():
    user = userRef()
    obstacleRef = user.moveInMap(1,0, obstacleObjRefs) 
    if obstacleRef is None:
        map.x -= 1   
    else:
        if obstacleRef().fighterComponent is not None:
            user.fighterComponent.attack(obstacleRef)
        else:
            print "but didn't try to break this shit!"

END_LOOP_TEST = 0
def endLoopTest():
    return END_LOOP_TEST

#### 입력 테이블 ####
proto1InputTable = {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):    userMoveUp, 
                    ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR):  userMoveDown,
                    ihdr.KeyTuple(libtcod.KEY_LEFT, ihdr.NOT_CHAR):  userMoveLeft,
                    ihdr.KeyTuple(libtcod.KEY_RIGHT, ihdr.NOT_CHAR): userMoveRight,
                    ihdr.KeyTuple(libtcod.KEY_ESCAPE, '\x1b'): endLoopTest}

##################################################################################


class Test_proto1(unittest.TestCase):
    def setUp(self):
        '''
        순서를 반드시 지켜야 한다.
        '''
        #1. 창 초기화
        font = gui.Font('font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        gset.setWindow(font, gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 'test')
        gset.setLimitFps(gset.LIMIT_FPS)

        #2. 맵에 스크린 배치
        global terrainScreen, mapObjScreen, npcScreen, userScreen, map
        
        map = Map.Map()
        terrainScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT, backAlphaRatio=1.0)
        mapObjScreen =  gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        npcScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        userScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        map.add(terrainScreen)
        map.add(mapObjScreen)
        map.add(npcScreen)
                   
        #3. 게임 오브젝트 생성 준비
        #반드시 이전에 정의한 리스트에 넣어야 게임오브젝트를 사용할 수 있다.
        # 아래 3.~들의 생성 순서는 기획에 따라 달라질 수 있다...만 맵을 먼저 배치하는 게 이치에 맞아보인다.
        global gameObjFactory
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())

        #3.~ 지형 생성
        for x in range(gset.WINDOW_WIDTH):
            for y in range(gset.WINDOW_HEIGHT):
                tileRefs[x][y] = gameObjFactory.createGameObject(lambda:createTile(x,y))
        #3.~ 맵 구성요소 생성 
        for i in range(13): 
            obstacleObjRefs.append( gameObjFactory.createGameObject(lambda:createTree(i)) )
        #3.~ 더미 적 생성
        dummyRef = gameObjFactory.createGameObject(createDummyEnemy)
        obstacleObjRefs.append(dummyRef)
        #3.~ 진짜 적 생성
        for i in range(4):
            enemyRef = gameObjFactory.createGameObject(createEnemy)
            obstacleObjRefs.append(enemyRef)
            enemyRefs.append(enemyRef)
        #3.~ 유저 생성
        global userRef 
        userRef = gameObjFactory.createGameObject(createUserPlayer)

        #테스트를 위한 특별 참조
        self.user = userRef()
        self.other = enemyRefs[0]()

        return super(Test_proto1, self).setUp()
                              
    def test_fighterDie(self):
        fighter = Fighter(10,1,1,1,1)
        fighter.hp = 0

    def test_isObstacleAt(self):
        obstacle = obstacleObjRefs[0]()
        self.assertTrue(isObstacleAt(obstacle.x, obstacle.y))
    
        '''
    #@unittest.skip('GameObjFactory.createGameObject')
    def test_obstacleMustDepositAtObstacleObjRefs(self):
        
        GameObjFactory.createGameObject를 안전하도록 고쳐라?
        그러려면 많은 것이 바뀌어야 한다.
        이 클래스는 게임오브젝트를 만드는 책임을 갖는다.
        
        역시 안 해야겠다. 지금 같은 구조라서 유연해질 수 있다.
        조금 위험하긴 하지만...

        beforeNum = len(obstacleObjRefs)
        self.assertEqual( len(obstacleObjRefs), beforeNum + 1, "create GameObject that have Obstacle component but didn't put its weakref at ObstacleRefs")
        '''

    def test_userAndOtherMoveMethodIsSame(self):        
        #유저와 ai를 움직이게 하는 입력의 결과(함수)는 동일하다.
        dx = 2
        dy = 1

        #유저 이동        
        userBeforeX = self.user.x
        userBeforeY = self.user.y
        self.user.move(dx, dy)
        self.assertEqualPositionInMap,(self.user, userBeforeX + dx, userBeforeY + dy)
        
        #적 이동        
        otherBeforeX = self.other.x
        otherBeforeY = self.other.y
        self.other.move(dx, dy)
        self.assertEqualPositionInMap,(self.other, otherBeforeX + dx, otherBeforeY + dy)
        
    def test_gameObjCannotMoveOverBlockedObj(self):
        #given: get obstacle ref
        obstacle = obstacleObjRefs[0]()
        #then: assert it is obstacle
        assert obstacle.obstacleComponent is not None

        dx = 2
        dy = 2        
        #given: user and obstacle.        
        userBeforeX = self.user.x
        userBeforeY = self.user.y
        obstacle.x = userBeforeX + dx
        obstacle.y = userBeforeY + dy        
        #when: user try to move over obstacle.        
        self.user.move(dx, dy)        
        #then: but user can't move over obstacle.
        self.assertEqualPositionInMap(self.user, userBeforeX, userBeforeY)
               
        #given: other player and obstacle
        otherBeforeX = self.other.x
        otherBeforeY = self.other.y
        obstacle.x = otherBeforeX + dx
        obstacle.y = otherBeforeY + dy
        #when: other player try to move over obstacle
        self.other.move(dx,dy)
        #then: but other player can't move over obstacle.
        self.assertEqualPositionInMap(self.other, otherBeforeX, otherBeforeY)
        
    def test_whenTurnEndsThenItsActCountMustBeZero(self):
        #given: someone's turnTaker component
        testInputTable = { ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): moveTestUpKey}
        key = libtcod.Key()
        ihandler = ihdr.InputHandler(key, testInputTable)

        maxCount = 5
        ttaker = TurnTaker(maxCount, ihandler)
        self.assertEqual(ttaker.maxActCount, maxCount)

        #when: turnTaker's turn 
        userPlayer = GameObject(0,0, turnTakerComponent=ttaker)
        key.vk = libtcod.KEY_UP; key.c = ord(ihdr.NOT_CHAR)
        ttaker.takeTurn()

        #then: since turnTaker's turn ends, then its actCount must be 0.
        self.assertEqual(ttaker.actCount, 0)
    '''
    @unittest.skip('maybe.. over engineering')
    def test_TurnTakerActAccordingToControlArgument(self):
        #given: 
        ttaker = TurnTaker(5)
        #when: 
        ttaker.act('move south')
        #then: 
    '''              

    def test_takeTurnToMoveDxDy(self):                
        testInputTable = {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):     moveTestUpKey,
                          ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR):   moveTestDownKey,
                          ihdr.KeyTuple(libtcod.KEY_LEFT, ihdr.NOT_CHAR):   moveTestLeftKey}
        key = libtcod.Key()
        ihandler = ihdr.InputHandler(key, testInputTable)
        
        #테스트용 inputTable이 연결된 TurnTaker를 가지는 유저객체 생성
        ttaker = TurnTaker(5, ihandler)
        userPlayer = GameObject(1,2, turnTakerComponent=ttaker)
        
        #given: UP key 입력시 이동하는 양                
        key.vk = libtcod.KEY_UP;    key.c = ord(ihdr.NOT_CHAR)
        self.assertPlayerPositionIncreasedDeltaXY(userPlayer, +5, +10)        
        #DOWN key 입력시 이동하는 양                
        key.vk = libtcod.KEY_DOWN;  key.c = ord(ihdr.NOT_CHAR)
        self.assertPlayerPositionIncreasedDeltaXY(userPlayer, -7, -14)
        #Left key 입력 5번(실제 게임의 이동과 비슷함) moveTestLeftKey
        key.vk = libtcod.KEY_LEFT;  key.c = ord(ihdr.NOT_CHAR)        
        self.assertPlayerPositionIncreasedDeltaXY(userPlayer, -5, 0)
    
    @unittest.skip("not yet")
    def test_takeTurnToMoveDxDyUsingUniformThing(self):
        testInputTable = {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):     moveTestUpKey,
                          ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR):   moveTestDownKey,
                          ihdr.KeyTuple(libtcod.KEY_LEFT, ihdr.NOT_CHAR):   moveTestLeftKey}
        key = libtcod.Key()
        ihandler = ihdr.InputHandler(key, testInputTable)
        
        #테스트용 inputTable이 연결된 TurnTaker를 가지는 유저객체 생성
        ttaker = TurnTaker(5, ihandler)
        userPlayer = GameObject(1,2, turnTakerComponent=ttaker)
        
        #given: UP key 입력시 이동하는 양                
        key.vk = libtcod.KEY_UP;    key.c = ord(ihdr.NOT_CHAR)
        self.assertPlayerPositionIncreasedDeltaXY(userPlayer, +5, +10)        
        #DOWN key 입력시 이동하는 양                
        key.vk = libtcod.KEY_DOWN;  key.c = ord(ihdr.NOT_CHAR)
        self.assertPlayerPositionIncreasedDeltaXY(userPlayer, -7, -14)
        #Left key 입력 5번(실제 게임의 이동과 비슷함) moveTestLeftKey
        key.vk = libtcod.KEY_LEFT;  key.c = ord(ihdr.NOT_CHAR)        
        self.assertPlayerPositionIncreasedDeltaXY(userPlayer, -5, 0)

    
                

    def assertPlayerPositionIncreasedDeltaXY(self, player, dx, dy):
        '''플레이어가 움직인 좌표의 양은 dx dy임을 단언한다.'''        
        beforeX = player.x
        beforeY = player.y
        #player move
        player.turnTakerComponent.takeTurn()                
        self.assertEqualPositionInMap(player, beforeX + dx, beforeY + dy)
            

    def assertEqualPositionInMap(self, obj, xInMap, yInMap):
        self.assertEqual(obj.x, xInMap, "obj.x :" + str(obj.x) + " != " + str(xInMap) + ": expected x")
        self.assertEqual(obj.y, yInMap, "obj.y :" + str(obj.y) + " != " + str(yInMap) + ": expected y")
           
    def test_allPlayersHasSameTurnTakingMethod(self):
        pass

    #이게 말하자면 인수테스트다. 최종적으로 실제로 작동하는지 확인한다.
    @unittest.skip('not now')
    def test_gameLoop(self):     
        self.fail("test TurnTaker in real game world!")
        #1. 입력 준비
        mouse = libtcod.Mouse()
        key = libtcod.Key()
        ihandler = ihdr.InputHandler(key,proto1InputTable)

        i = 0
        while not libtcod.console_is_window_closed():
            # 사용자 입력
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
            inputResultFunc = ihandler.inputResult()

            # 사용자 입력이 없는데 적들이 멋대로 움직이면 안 된다.
            # 근데 입력은 유저 플레이어.takeTurn 에서 대기해야 할 텐데.?
            # 마우스 입력 때문에... 반드시 끊임 없는 이벤트를 받아야 한다.

            #
            
            test_output = None
            if inputResultFunc is not None:
                # 유저의 턴: 입력에 따른 게임 상태 변화
                test_output = inputResultFunc()
                # 적들의 턴
                for enemyRef in enemyRefs:
                    enemyRef().takeTurn(obstacleObjRefs) #유저도 동일한 메서드를 써야할 거 같다.

            if test_output == END_LOOP_TEST:
                #only for test
                print "pressed ESC to end main loop test!"
                break
            
            # 렌더링
            # ■■■버퍼 지우기■■■
            libtcod.console_clear(0) 
            map.renderAndBlit()
            userScreen.renderAndBlit()            
            # ■■■버퍼 비우기■■■
            libtcod.console_flush() 
     
        

############## 테스트용 입력테이블 대응 함수 ##############
def moveTestUpKey(user):
    user.move(5,10)
    return 5

def moveTestDownKey(user):
    user.move(-7,-14)
    return 7
        
def moveTestLeftKey(user):
    ''' 
    왼쪽으로 한 칸 움직이는데 
    :returns: 행동력 1이 필요하다. 
    '''
    user.move(-1,0)
    return 1

def pseudoInputTest(user, dx, dy, actCost):
    user.move(dx, dy)
    return actCost        

if __name__ == '__main__':
    unittest.main()
