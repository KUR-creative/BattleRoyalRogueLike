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
from brrl_proto1 import TurnSystem as tsys
from brrl_proto1 import utilities as util

#이 임포트 구문이 사라지면 모듈화가 완료된 것이다.
import game_state_changer_test1 as gsch

semanticInputs = util.enum('UP', 'DOWN', 'LEFT', 'RIGHT', 'SKIP', 'EXIT')  

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
    if getObstacleAt(x,y, obstacleObjRefs):
        x += 1
    rCompo = gui.RenderObject(npcScreen,'enemy',u'적', 
                                  x,y,
                                  foreColor=libtcod.blue)
    obsCompo = gsch.Obstacle(True)
    fCompo = gsch.Fighter(30,10)
    tCompo = gsch.TurnTaker(1)
    return gsch.GameObject(x, y, 
                           renderComponent=rCompo, 
                           obstacleComponent=obsCompo,
                           fighterComponent=fCompo,
                           turnTakerComponent=tCompo,
                           stateChangerComponent=proto1StateChangerCompo())

def createFovEffects(x,y):    
    cell = gui.RenderObject(fovScreen,
                            'fovCell'+ str(x+y), ' ',
                            x,y, foreColor=libtcod.black, backColor=libtcod.black)
    return gsch.GameObject(x,y, cell)

def createUserPlayer():       
    initX = 4
    initY = gset.WINDOW_HEIGHT/2
    rCompo = gui.RenderObject(userScreen,'user',u'나', 
                              initX,initY,
                              foreColor=libtcod.black)
    obsCompo = gsch.Obstacle(True)
    fCompo = gsch.Fighter(30,5)
    tCompo = gsch.TurnTaker(2)
    return gsch.GameObject(initX, initY,                            
                           renderComponent=rCompo, 
                           obstacleComponent=obsCompo,
                           fighterComponent=fCompo,
                           turnTakerComponent=tCompo,
                           stateChangerComponent=proto1StateChangerCompo())


######## 100% 게임로직 됨 game logic(game specific) ########

class proto1StateChangerCompo(object):
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
    
    def changeState(self, semanticInput):
        if semanticInput is None:
            return None        
        
        if semanticInput == semanticInputs.UP:
            self.moveOrMeleeAttack(0, -1)
        elif semanticInput == semanticInputs.DOWN:
            self.moveOrMeleeAttack(0, +1)
        elif semanticInput == semanticInputs.LEFT:
            self.moveOrMeleeAttack(-1, 0)
        elif semanticInput == semanticInputs.RIGHT:
            self.moveOrMeleeAttack(+1, 0)

        #recompute fov!
        computeFov(self.owner.x, self.owner.y, 15)      
        #render fov!
        if self.owner == userRef():
            for y in range(gset.WINDOW_HEIGHT):
                for x in range(gset.WINDOW_WIDTH):
                    #TODO: 이것도 전역변수보단 나중에 생성자에서 주입해줘야겠지.
                    fovEffect = fovEffectRefs[x][y]()
                    if libtcod.map_is_in_fov(fov_map, x, y):
                        #fovEffect = gsch.GameObject()
                        fovEffect.renderCompo.char = ' '
                        fovEffect.renderCompo.backColor = libtcod.white
                    else:
                        fovEffect.renderCompo.char = ' '
                        fovEffect.renderCompo.backColor = libtcod.black

        if semanticInput == semanticInputs.SKIP:
            self.owner.skip()

        if semanticInput == semanticInputs.EXIT:
            return semanticInput 
    
    def moveOwner(self, dx, dy):
        #TODO: maybe refactor.. 저거 장애물참조리스트 이 객체 만들 때 집어넣어 주는게 낫겠지 아무래도?        
        adjacentObstacle = getObstacleAt(self.owner.x + dx, self.owner.y + dy, obstacleObjRefs)
        if adjacentObstacle is None:
            self.owner.move(dx, dy)      
                                             
        else:
            print "cannot move over blocked obstacle!"  
            return adjacentObstacle

    def moveOrMeleeAttack(self, dx, dy):
        #장애물이 없으면 움직인다.
        adjacentObstacle = self.moveOwner(dx, dy)
        if(adjacentObstacle is not None and #장애물이 있는데
           adjacentObstacle.fighterCompo is not None):
            #공격 가능하면 공격한다.
            self.owner.fighterCompo.attack(adjacentObstacle.fighterCompo)

'''
class proto1FovManagerStateChanger(object):
    def __init__(self, fovEffectRefList):
        self.fovEffectRefs = fovEffectRefList

    def changeState(self, semanticInput):
        self.owner.turnTakerCompo.actCount = 0
        print ' >>><<< '
        for y in range(gset.WINDOW_HEIGHT):
            for x in range(gset.WINDOW_WIDTH):
                fovEffect = self.fovEffectRefs[x][y]()
                if libtcod.map_is_in_fov(fov_map, x, y):
                    #fovEffect = gsch.GameObject()
                    fovEffect.renderCompo.char = ' '
                else:
                    fovEffect.renderCompo.char = '*'

class proto1FovManagerAi(object):
    def calcNextAct(self, nowGameState):
        return 'do fov'
'''

inputTable = {ihdr.KeyTuple(libtcod.KEY_ESCAPE, '\x1b'):      semanticInputs.EXIT,
              ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):   semanticInputs.UP,
              ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): semanticInputs.DOWN,
              ihdr.KeyTuple(libtcod.KEY_LEFT, ihdr.NOT_CHAR): semanticInputs.LEFT,
              ihdr.KeyTuple(libtcod.KEY_RIGHT, ihdr.NOT_CHAR):semanticInputs.RIGHT} 


class proto1OnlyUpAi(object):
    def calcNextAct(self, nowGameState):
        return semanticInputs.UP
class proto1OnlyDownAi(object):
    def calcNextAct(self, nowGameState):
        return semanticInputs.DOWN
class proto1OnlySkipAi(object):
    def calcNextAct(self, nowGameState):
        return semanticInputs.SKIP



################################

#여기도 나중에 모듈로 옮겨라.
def getObstacleAt(xInMap, yInMap, obstacleObjRefs):
    '''
    입력된 좌표에 장애물이 있다면 반환한다.

    :param int xInMap: 알고 싶은 맵의 x좌표
    :param int yInMap: 알고 싶은 맵의 y좌표
    :param weakref obstacleObjRefs: 장애물 약한참조가 있는 리스트

    :returns: Obstacle이 있으면 그 obstacle 반환 / 없으면 None
    '''
    for obstacleRef in obstacleObjRefs:
        obstacle = obstacleRef()
        if(obstacle.obstacleCompo.blocked and
           obstacle.x == xInMap and
           obstacle.y == yInMap):
            return obstacleRef()
    return None

#### 약한 참조 저장소 ####
# 적절한 용도에 따라 임시로 저장하고 쓰는 저장소이다.
# 약한참조만을 가질 뿐 GameObject에 대한 소유권을 갖지 않는다.
#
#지형 저장소
tileRefs = [[None
                for y in range(gset.WINDOW_HEIGHT)]
                for x in range(gset.WINDOW_WIDTH)]
#막아서는 놈들 저장소: 반드시 여기에 저장되는게 보장되어야 한다.(버그가 없으려면)
obstacleObjRefs = []
#적
enemyRefs = []
#fov effects
fovEffectRefs = [[None
                    for y in range(gset.WINDOW_HEIGHT)]
                    for x in range(gset.WINDOW_WIDTH)]
#유저
userRef = None

#FOV 적용하기.
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True
RADIUS = 10

fov_map = libtcod.map_new(gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT)
libtcod.map_clear(fov_map, transparent=True, walkable=True)
def computeFov(x, y, radius, lightWalls=True):
    libtcod.map_compute_fov(fov_map, x,y, radius, lightWalls,FOV_ALGO)

class Test_prototype1(unittest.TestCase):
    def test_prototype1(self):
        #창 초기화
        font = gui.Font('font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        gset.setWindow(font, gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 'test')
        gset.setLimitFps(gset.LIMIT_FPS)

        #맵에 스크린 배치(TODO: 전역객체를 없애는게 좋지 않을까?)
        global terrainScreen, mapObjScreen, npcScreen, userScreen, fovScreen

        self.map = Map.Map()
        terrainScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT, backAlphaRatio=1.0)
        mapObjScreen =  gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        npcScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        fovScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT, backAlphaRatio=0.5)
        userScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        self.map.add(terrainScreen)
        self.map.add(mapObjScreen)
        self.map.add(npcScreen)
        self.map.add(fovScreen)
        
        #게임 오브젝트 생성 준비
        global gameObjFactory
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
                        
        # 지형 생성
        for x in range(gset.WINDOW_WIDTH):
            for y in range(gset.WINDOW_HEIGHT):
                tileRefs[x][y] = gameObjFactory.createGameObject(lambda:createTile(x,y))
        # 맵 구성요소 생성 
        for i in range(13): 
            gameObjFactory.createGameObject(lambda:createTree(i), obstacleObjRefs)
        
        # 적 생성
        for i in range(4):
            enemyRef = gameObjFactory.createGameObject(lambda:createEnemy(i*10, i*5),
                                                       obstacleObjRefs, enemyRefs)
            
        # 시야 효과 생성
        for x in range(gset.WINDOW_WIDTH):
            for y in range(gset.WINDOW_HEIGHT):
                fovEffectRefs[x][y] = gameObjFactory.createGameObject(lambda:createFovEffects(x,y))

        '''
        # 관리자 객체(사실 fov관리는 여기서 안 해..)
        fovManTTaker = gsch.TurnTaker(1)
        fovManSChanger = proto1FovManagerStateChanger(fovEffectRefs)
        fovManager = gsch.GameObject(-1,-1,
                                     turnTakerComponent=fovManTTaker,
                                     stateChangerComponent=fovManSChanger)
        '''
        # 유저 생성
        global userRef 
        userRef = gameObjFactory.createGameObject(createUserPlayer, obstacleObjRefs)
        user = userRef()

        #fov map 처리
        for obsRef in obstacleObjRefs:
            obstacle = obsRef()
            #obstacleObjRefs에 있는 모든 게임객체가 시야를 가리는건 아냐.
            #libtcod.map_set_properties(fov_map, obstacle.x, obstacle.y, obstacle.obstacleCompo.blocked, True)
            libtcod.map_set_properties(fov_map, obstacle.x, obstacle.y, False, True)
        
        #입력 준비        
        self.key = libtcod.Key()

        #유저와 인공지능과 플레이어(gobj)와 매니저
        playerList = [user, 
                      enemyRefs[0](), enemyRefs[1](), enemyRefs[2](), enemyRefs[3]()]                      
        userList = [ihdr.InputHandler(self.key, inputTable),
                    ihdr.AiInputHandler(playerList[0], proto1OnlyDownAi()),
                    ihdr.AiInputHandler(playerList[1], proto1OnlyUpAi()),
                    ihdr.AiInputHandler(playerList[2], proto1OnlySkipAi()),
                    ihdr.AiInputHandler(playerList[3], proto1OnlyDownAi()) ]
                        
        turnSystem = tsys.TurnSystem(userList, playerList, 
                                     self.map,
                                     userScreen)
                        
        #게임 루프
        while not libtcod.console_is_window_closed():
            #턴 시스템 작동.
            exit = turnSystem.run()

            if exit == semanticInputs.EXIT:
                break

######## Fighter Tests(TODO:나중에 모듈 분리되면 이것도 테스트모듈 새로 만들고 옮겨야 함.) ########
#
    def setUp(self):
        self.hp = 10
        atk = 2
        
        def createPlayer():
            fighter = gsch.Fighter(self.hp, atk)
            player = gsch.GameObject(1,1,
                                     turnTakerComponent=gsch.TurnTaker(5),
                                     renderComponent=gui.RenderObject(None, '1', '@', 1,1),
                                     obstacleComponent=gsch.Obstacle(True),
                                     fighterComponent=fighter)
            return player

        def createOther():
            otherFighter = gsch.Fighter(self.hp, atk)
            other = gsch.GameObject(2,2,
                                    turnTakerComponent=gsch.TurnTaker(5),
                                    renderComponent=gui.RenderObject(None, '2', '@', 2,2),
                                    obstacleComponent=gsch.Obstacle(True),
                                    fighterComponent=otherFighter)
            return other

        self.gObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
        
        global obstacleObjRefs
        playerRef = self.gObjFactory.createGameObject(createPlayer, obstacleObjRefs)
        self.player = playerRef()
        otherRef = self.gObjFactory.createGameObject(createOther, obstacleObjRefs)
        self.other = otherRef()
        
    def tearDown(self):
        #clear obstacles.
        del obstacleObjRefs[:]

        return super(Test_prototype1, self).tearDown()

    def test_fighterCanAttack(self):
        #given: 
        hp = self.other.fighterCompo.hp
        atk = self.player.fighterCompo.power
        #when: fight
        self.player.fighterCompo.attack(self.other.fighterCompo)
        #then: hp 감소
        self.assertEqual(self.other.fighterCompo.hp, hp - atk)

    def test_fighterCanDeath(self):
        #given: player can kill other
        self.player.fighterCompo.power = self.hp + 5
        #when: attack
        self.player.fighterCompo.attack(self.other.fighterCompo)
        #then: target is dead - it isn't Obstacle any more.
        self.assertLessEqual(self.other.fighterCompo.hp, 0)
        self.assertFalse(self.other.obstacleCompo.blocked)

    def test_placeCorpseWhenPlayerDie(self):
        '''
        근데 이거 알고리즘이 달라질 수 있는데..
        일단 해본다.
        '''
        #given: a player
        corpse = 'X'
        self.player.fighterCompo.corpseChar = corpse
        #when: the player is dead
        self.player.fighterCompo.die()
        #then: character of player change corpse char
        self.assertEqual(self.player.renderCompo.char, corpse)
        
        #given: other player, other corpse
        otherCorpse = '%'        
        self.other.fighterCompo.corpseChar = otherCorpse
        #when: other player is dead
        self.other.fighterCompo.die()
        #then: character of player change corpse char
        self.assertEqual(self.other.renderCompo.char, otherCorpse)
                    
    def test_deadPlayerCannotAct(self):
        beforeY = self.player.y
        #given: dead player
        self.player.fighterCompo.die()
        #when: dead player try to act 
        try:
            self.player.move(0,1)
        except AssertionError:
            #행동력을 없애서 못움직이게 한다.
            pass
        #then: but can't act
        self.assertEqual(self.player.y, beforeY)
                
        #given: 턴이 지났을 때 행동력을 회복시킴
        self.player.turnTakerCompo.actCount = self.player.turnTakerCompo.maxActCount
        #when: 움직일 수 있나?
        try:
            self.player.move(0,1)
        except AssertionError:
            #행동력을 없애서 못움직이게 한다.
            pass
        #then: 못 움직임
        self.assertEqual(self.player.y, beforeY)
                
    def test_playerMustConsumeToAttackSomething(self):
        #given: 
        beforeActCount = self.player.turnTakerCompo.actCount
        actCost = 1
        #when: 
        self.player.fighterCompo.attack(self.other.fighterCompo)
        #then: 
        self.assertEqual(self.player.turnTakerCompo.actCount, beforeActCount - actCost)

    def test_playerCanMoveOrAttackWhenTargetObjAdjoinsPlayer(self):        
        beforeTargetHp = self.other.fighterCompo.hp
        atk = self.player.fighterCompo.power
        
        #given: plug stateChangerComponent into player, place adjacent target 
        self.player.stateChangerCompo = self.player.setOwnerOf(proto1StateChangerCompo())

        #1.when: 장애물이 근처에 없음
        beforeY = self.player.y
        self.other.x = self.player.x + 2
        self.other.y = self.player.y + 2
        self.player.stateChangerCompo.moveOrMeleeAttack(0,-1)        
        #then: 이동 가능
        self.assertEqual(self.player.y, beforeY - 1)
        
        #2.when: 장애물이 있어 이동 불가, 그 장애물이 공격 가능
        beforeY = self.player.y
        self.other.x = self.player.x
        self.other.y = self.player.y + 1
        self.player.stateChangerCompo.moveOrMeleeAttack(0,+1)        
        #then: player can't move, attack the target
        self.assertEqual(self.player.y, beforeY)
        self.assertEqual(self.other.fighterCompo.hp, beforeTargetHp - atk)
    
        #3.when: 장애물이 있어 이동 불가, 그 장애물은 공격 불가
        beforeY = self.player.y
        def createTempObstacle():
            return gsch.GameObject(self.player.x, self.player.y + 1,
                                   obstacleComponent=gsch.Obstacle(True))
        self.gObjFactory.createGameObject(createTempObstacle, obstacleObjRefs)
        #then: player can't move
        self.player.stateChangerCompo.moveOrMeleeAttack(0,+1)        
        self.assertEqual(self.player.y, beforeY)

    def test_corpseIsNotObstacle(self):        
        # get before values
        beforeY = self.player.y
        beforeTargetHp = self.other.fighterCompo.hp
        atk = self.player.fighterCompo.power
        
        #given: player and other adjacent player
        self.player.stateChangerCompo = self.player.setOwnerOf(proto1StateChangerCompo())
        self.other.x = self.player.x
        self.other.y = self.player.y + 1
        #when: player can attack other adjacent player
        self.player.stateChangerCompo.moveOrMeleeAttack(0,+1)        
        #then: so player don't move but attack. because living player is obstacle.
        self.assertEqual(self.player.y, beforeY)
        self.assertEqual(self.other.fighterCompo.hp, beforeTargetHp - atk)

        #given: kill other adjacent player
        beforeTargetHp = self.other.fighterCompo.hp
        self.other.fighterCompo.die()
        #when: player try to move over corpse
        self.player.stateChangerCompo.moveOrMeleeAttack(0,+1)        
        #then: it works.
        self.assertEqual(self.player.y, beforeY + 1)
        self.assertEqual(self.other.fighterCompo.hp, beforeTargetHp)
        

if __name__ == '__main__':
    unittest.main()
