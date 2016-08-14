#-*- coding: utf-8 -*-
'''
이 모듈의 테스트들은 모두 구체적이고 암묵적인 [값]에 의존하고 있다.
회귀테스트에서 쓰려면 그래서는 안 된다. 
지금까지 테스트에 쓰인 모든 [값]들을 어딘가에 모아두어야 한다.
또 게임 로직은 매우 쉽게 변하는 부분인데, 
GameStateChanger와 GameObject에 퍼져서 있다.
이 로직을 분리해야 한다...

원시 입력 -> 의미적 입력(semanticInput) -> 상태변화(state change, inputResult)

'''

import unittest
import libtcodpy as libtcod

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import GameObjectFactory as gfac
from brrl_proto1 import GameObjectRepository as grepo

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import input_handler as ihdr


class Obstacle:
    def __init__(self, blocked=False):      
        self.blocked = blocked

def createObstacle(x, y):
    mCompo = Obstacle(True)
    return GameObject(x, y, obstacleComponent=mCompo)
        

obstacleObjRefs = []

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


class TurnTaker(object):
    def __init__(self, maxActCount, inputSource=None):
        self.maxActCount = maxActCount        
        self._actCount = maxActCount

        self.inputSource = inputSource
    
    @property
    def actCount(self):
        return self._actCount

    @actCount.setter
    def actCount(self, val):        
        assert (val >= 0 and "player's actCount is negative number. FATAL error!")
        self._actCount = val

                                
class GameObject:
    '''
    테스트용 fake객체.
    '''
    def __init__(self, xInMap, yInMap, 
                 renderComponent=None, 
                 obstacleComponent=None, 
                 fighterComponent=None,
                 turnTakerComponent=None,
                 canPenetrate=False,
                 moveCost=1):
        self.x = xInMap
        self.y = yInMap
        self.canPenetrate = canPenetrate
        self.moveCost = moveCost

        #리스트에 컴포넌트들을 집어넣고 enum을 만드는 식으로 리팩토링 가능.
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

    # 게임 오브젝트는 할 수 있는 일들이 다르다.
    # 메서드로 하기에는 좀... 메서드는 너무 정적이다. 이걸 어떻게 리팩토링하는가?
    def move(self, dx, dy):        
        self.x += dx
        self.y += dy
        self.turnTakerComponent.actCount -= self.moveCost # 이 값은 어떻게 리팩토링하지?

    def skip(self):
        self.turnTakerComponent.actCount = 0

    def inputS(self):
        self.turnTakerComponent.actCount -= 2

    def inputA(self):
        if self.weapon == 'gun':
            self.turnTakerComponent.actCount -= 2
        else:
            self.turnTakerComponent.actCount -= 1


class GameStateChanger(object):
    def __init__(self, inputHandler, player):
        self.player = player
        self.inputHandler = inputHandler

    def setInputTable(self, inputTable):
        self.inputHandler.inputTable = inputTable

    def inputResult(self):
        assert (self.player.turnTakerComponent.actCount != 0 and 
                "accepted input but player's actCount is 0!")
        
        semanticInput = self.inputHandler.inputResult()
        #리팩토링이 필요하다. 
        #원시입력기(inputHandler), 유저, 장애물 목록 등 
        #다양한 상태에 따라 다양한 반응이 필요하다. 즉, 매우 변화가 잦은 부분이다.
        if semanticInput is None: #입력이 없다
            return

        elif semanticInput == 'skip': 
            self.player.skip()
        
        elif semanticInput == 'up':
            self.player.move(0, -1)
        
        elif semanticInput == 'down':
            #모든 move에 장애물 뚫기 테스트를 적용해야 한다.
            #gameObj 종류에 따라 장애물을 뚫을 수도 있다.
            #isObstacleAt함수는 안 좋다. 이 클래스에 주입되지 않은 외부 환경을 참조하니까.
            if(isObstacleAt(self.player.x + 0, self.player.y + 1) and 
               not self.player.canPenetrate ):
                print "cannot move over blocked obstacle!"  
            else:
                self.player.move(0, +1)
        
        elif semanticInput == 's': 
            #모든 종류의 행동에 대해 적용해야 한다. actCost = 0 인 행동도 있다.
            #입력 S의 actCost는 2이다. 
            #그런데.. GameObj의 inputS에 있는 2와 전혀 상관이 없다.        
            # 상관 있게 만들어야 한다.
            if self.player.turnTakerComponent.actCount > 2:
                self.player.inputS()

        elif semanticInput == 'a':
            #이것도 무기 클래스를 만들어야 하겠지.
            self.player.inputA()


            

class Test_game_state_changer(unittest.TestCase):
    def setUp(self):
        self.key = libtcod.Key()
        
        self.initMaxActCount = 5
        ttaker = TurnTaker(self.initMaxActCount)
        self.userPlayer = GameObject(1,2, turnTakerComponent=ttaker)
        
        #원시입력핸들러와 게임상태변경자 연결
        testInputTable = dict()        
        ihandler = ihdr.InputHandler(self.key, testInputTable)        
        self.stateChanger = GameStateChanger(ihandler, self.userPlayer)
        
        return super(Test_game_state_changer, self).setUp()

    def test_noInputNoStateChange(self):                    
        #given: no available input(default inputTable in setUp())        
        #when: no input 
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        self.stateChanger.inputResult()        
        #then: no change
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, beforeActCount)
                
    def test_inputSomeKeyToSkipTurnOfPlayer(self):
        #given: 스페이스바로 스킵, 게임 상태를 상태변화자에게 전달
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): 'skip'}
        )
        
        #when: 스페이스바를 누르면(가짜 입력)
        self.pseudoKeyInput(libtcod.KEY_SPACE,' ')
        self.stateChanger.inputResult()
        
        #then: 행동력이 모두 소모됨
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 0)

    def test_inputSomeKeyToMoveGameObj(self):
        #이전 값
        beforeX = self.userPlayer.x
        beforeY = self.userPlayer.y
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        
        #given: UP key로 위로 1칸 이동
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): 'up'}
        )

        #when: UP key를 누르면
        self.pseudoKeyInput(libtcod.KEY_UP, ihdr.NOT_CHAR)
        self.stateChanger.inputResult()

        #then: 위로 1칸 이동함. 행동력 감소
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY - 1)
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, beforeActCount - 1)
        

        #given: 다른 게임 오브젝트 움직이기(사실 뻔함)
        ttaker = TurnTaker(5)
        otherPlayer = GameObject(1,2, turnTakerComponent=ttaker)
        self.stateChanger.player = otherPlayer

        #이전 값
        beforeX = otherPlayer.x
        beforeY = otherPlayer.y
        beforeActCount = otherPlayer.turnTakerComponent.actCount
        
        #when: 
        self.pseudoKeyInput(libtcod.KEY_UP, ihdr.NOT_CHAR)        
        self.stateChanger.inputResult()

        #then: 위로 1칸 이동함. 행동력 감소
        self.assertEqualPositionInMap(otherPlayer, beforeX + 0, beforeY - 1)
        self.assertEqual(otherPlayer.turnTakerComponent.actCount, beforeActCount - 1)
    
    def test_cannotMoveOverObstacle(self):
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): 'down'}
        )

        #변화 이전 값
        beforeX = self.userPlayer.x
        beforeY = self.userPlayer.y
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        
        #given: userPlayer 한 칸 아래에 장애물 놓기.
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
        obstacleObjRefs.append(
            gameObjFactory.createGameObject( 
                lambda:createObstacle(beforeX, beforeY + 1) 
            )
        )
                   
        #when: DOWN key를 누르면
        self.pseudoKeyInput(libtcod.KEY_DOWN,ihdr.NOT_CHAR)        
        self.stateChanger.inputResult()

        #then: 행동력 감소 안 함. 아래로 1칸 이동 못함. 
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, beforeActCount)
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)

    def test_someGameObjCanPenetrateObstacles(self):        
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): 'down'}
        )

        #변화 이전 값
        someObj = self.userPlayer        
        beforeX = someObj.x
        beforeY = someObj.y
        
        #given: someObj 한 칸 아래에 장애물 놓기.
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
        obstacleObjRefs.append(
            gameObjFactory.createGameObject( 
                lambda:createObstacle(beforeX, beforeY + 1) 
            )
        )            
        someObj.canPenetrate = True  #장애물을 관통 가능한 객체.
        
        #when: DOWN key를 두번 누르면 
        self.pseudoKeyInput(libtcod.KEY_DOWN,ihdr.NOT_CHAR)        
        self.stateChanger.inputResult()
        self.stateChanger.inputResult() #두번.

        #then: 객체는 2칸을 내려감.
        self.assertEqualPositionInMap(someObj, beforeX, beforeY + 2)
       
    def test_noChangeWhenActCostOfSomethingIsMoreThanMaxActCountOfPlayer(self):        
        #given: setup시의 maxActCount는 5이고, s를 누르면 행동력 2가 까이는 행동을 함.
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(ihdr.NOT_VK, 's'): 's'}
        )
        #when: 입력이 3번 들어오면 2번까지는 동작하나 마지막은 불가능.
        self.pseudoKeyInput(ihdr.NOT_VK,'s')
                       
        #then: 행동력은 5 -> 's' -> 3 -> 's' -> 1 -> 's' -> 1 이 됨. 
        self.stateChanger.inputResult() 
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 3)
        self.stateChanger.inputResult() 
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 1)
        self.stateChanger.inputResult() # 3번의 입력, 마지막은 변화 없음.
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 1)
                            
    def test_sameInputToMoveButDifferentActCostEachPlayers(self):
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): 'up'}
        )
        #given: 움직임의 actCost가 2인 플레이어
        ttaker = TurnTaker(5)
        otherPlayer = GameObject(1,2, turnTakerComponent=ttaker, moveCost=2)
        
        self.stateChanger.player = otherPlayer

        #when: 위로 이동
        self.pseudoKeyInput(libtcod.KEY_UP,ihdr.NOT_CHAR)        
        beforeX = otherPlayer.x
        beforeY = otherPlayer.y
        beforeActCount = otherPlayer.turnTakerComponent.actCount

        self.stateChanger.inputResult()

        #then: 위로 1칸 이동함. 행동력 2개 감소
        self.assertEqualPositionInMap(otherPlayer, beforeX + 0, beforeY - 1)
        self.assertEqual(otherPlayer.turnTakerComponent.actCount, beforeActCount - 2)
    
    def test_sameInputButDifferentAttackIfPlayerHaveWeapon(self):
        #setUp: 'a' 입력 가능
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(ihdr.NOT_VK, 'a'): 'a'}
        )
        
        #given: weapon 총을 가진 플레이어        
        self.userPlayer.weapon = 'gun'
        #when: 버튼 a를 눌러 공격
        self.pseudoKeyInput(ihdr.NOT_VK,'a')        
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        self.stateChanger.inputResult()        
        #then: 총은 공격시에 행동력 2개 쓴다
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, beforeActCount - 2)
        
        #given: weapon 총을 갖지 않은 플레이어
        self.userPlayer.weapon = None
        #when: 버튼 a를 눌러 공격
        self.pseudoKeyInput(ihdr.NOT_VK,'a')        
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        self.stateChanger.inputResult()        
        #then: 그냥 공격에 행동력 1개 쓴다
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, beforeActCount - 1)
            
    def test_pseudoUserInputAndTurnTaking(self):
        ''' 
        실제 게임에 있을 법한 턴처럼 구성된 테스트
        입력없음 -> 입력 -> 입력없음 -> 입력... 
        '''
        self.stateChanger.setInputTable(            
             {ihdr.KeyTuple(ihdr.NOT_VK, 's'): 's',
              ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): 'up',
              ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): 'skip'}
        )        

        utTaker = self.userPlayer.turnTakerComponent

        #이전 값
        beforeX = self.userPlayer.x
        beforeY = self.userPlayer.y
        beforeActCount = utTaker.actCount
        # None 입력
        for times in range(10000):
            self.stateChanger.inputResult()
        #입력 결과
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
        self.assertEqual(utTaker.actCount, beforeActCount)

        #이전 값
        beforeX = self.userPlayer.x
        beforeY = self.userPlayer.y
        beforeActCount = utTaker.actCount
        # 'a' 입력        
        self.pseudoKeyInput(ihdr.NOT_VK, 's')
        self.stateChanger.inputResult()
        #입력 결과
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
        self.assertEqual(utTaker.actCount, beforeActCount - 2)

        #이전 값
        beforeX = self.userPlayer.x
        beforeY = self.userPlayer.y
        beforeActCount = utTaker.actCount
        # 'up' 입력
        self.pseudoKeyInput(libtcod.KEY_UP, ihdr.NOT_CHAR)
        self.stateChanger.inputResult()
        #입력 결과
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY - 1)
        self.assertEqual(utTaker.actCount, beforeActCount - 1)

    def test_inputButActCountOfPlayerIsZero(self):
        #given: 
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): 'skip'}
        )                
        #when: 스킵해서 현재 stateChanger의 플레이어 행동력이 0 만들기.
        self.pseudoKeyInput(libtcod.KEY_SPACE,' ')
        self.stateChanger.inputResult()             
        #then: 행동력이 0인데 입력이 들어오는 것은 비정상적인 작동이다.
        self.assertRaises(AssertionError, self.stateChanger.inputResult)

    def test_raiseErrorWhenActCountOfPlayerIsNegativeNumber(self):    
        try:
             self.stateChanger.player.turnTakerComponent.actCount = -1
        except AssertionError, e:    
            pass
        else:
            self.fail("AssertionError didn't raiesd")
                        
                                               
    def pseudoKeyInput(self, vk, c):
        assert type(vk) is int
        assert type(c) is str

        self.key.vk = vk 
        self.key.c = ord(c)

    def assertEqualPositionInMap(self, obj, xInMap, yInMap):
        self.assertEqual(obj.x, xInMap, "obj.x :" + str(obj.x) + " != " + str(xInMap) + ": expected x")
        self.assertEqual(obj.y, yInMap, "obj.y :" + str(obj.y) + " != " + str(yInMap) + ": expected y")
    


if __name__ == '__main__':
    unittest.main()
