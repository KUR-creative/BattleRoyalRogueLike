#-*- coding: utf-8 -*-
'''
이 모듈의 테스트들은 모두 구체적이고 암묵적인 [값]에 의존하고 있다.
회귀테스트에서 쓰려면 그래서는 안 된다. 
지금까지 테스트에 쓰인 모든 [값]들을 어딘가에 모아두어야 한다.
또 게임 로직은 매우 쉽게 변하는 부분인데, 
GameStateChanger와 GameObject에 퍼져서 있다.
이 로직을 분리해야 한다...

원시 입력 -> 의미적 입력(semanticInput) -> 상태변화(state change, inputResult)
입력 - stateChanger.updateStates()가 호출되기 전에 
서로 다른 입력이 3개 들어와 버리면 마지막 입력만 영향을 주게 된다...

현재 GameObject는 fake객체이다. 이거는 이 테스트 모듈 내에서만 쓰일 수 있다.
테스트에서만 쓰일 법한 부분을 게임 로직으로 분리해 내라.


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

class AI(object):
    def __init__(self, gameObj=None, agent=None):
        self.gameObj = gameObj
        self.agent = agent

    def getSemanticInput(self):
        '''
        이 함수에서 artificial intelligence를 구현할 수 있다.
        '''
        gObjState = self.gameObj.getAvailableStates()
        if gObjState == 'ai test':
            # 이 조건문들이 바로 판단하는 ai이다!
            if self.agent == 'only up':
                return 'up'
            if self.agent == 'only down':
                return 'down'
            if self.agent == 'only skip':
                return 'skip'
        else:
            return gObjState

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
        self.fakeState = None      

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

    
    #TODO:리팩토링 필요.    
    def getAvailableStates(self):
        '''
        게임오브젝트 사용자(유저/AI)에게 전달하는 게임오브젝트의 상태들
        이후 실제 게임에서 전달될 변수들이 결정되며 이걸 기준으로 렌더링도 함.
        전달용 클래스가 있어야 할지도 몰라.
        이후에 GameObject를 새로 작성할 때 반드시 바뀌어야 한다.
        '''
        #실제로는 이름과 아무 상관 없는 이상한 구현이다.
        #그저 내부의 상태를 사용하는 것 뿐..
        return self.fakeState         


class GameStateChanger(object):
    def __init__(self, inputHandler, gameObj):
        self.gameObj = gameObj
        self.inputHandler = inputHandler

    def setInputTable(self, inputTable):
        self.inputHandler.inputTable = inputTable

    def updateStates(self):
        assert (self.gameObj.turnTakerComponent.actCount != 0 and 
                "accepted input but player's actCount is 0!")
        
        semanticInput = self.inputHandler.getSemanticInput()
        #리팩토링이 필요하다. 
        #원시입력기(inputHandler), 유저, 장애물 목록 등 
        #다양한 상태에 따라 다양한 반응이 필요하다. 즉, 매우 변화가 잦은 부분이다.
        if semanticInput is None: #입력이 없다
            return

        elif semanticInput == 'skip': 
            self.gameObj.skip()
        
        elif semanticInput == 'up':
            self.gameObj.move(0, -1)
        
        elif semanticInput == 'down':
            #모든 move에 장애물 뚫기 테스트를 적용해야 한다.
            #gameObj 종류에 따라 장애물을 뚫을 수도 있다.
            #isObstacleAt함수는 안 좋다. 이 클래스에 주입되지 않은 외부 환경을 참조하니까.
            if(isObstacleAt(self.gameObj.x + 0, self.gameObj.y + 1) and 
               not self.gameObj.canPenetrate ):
                print "cannot move over blocked obstacle!"  
            else:
                self.gameObj.move(0, +1)
        
        elif semanticInput == 's': 
            #모든 종류의 행동에 대해 적용해야 한다. actCost = 0 인 행동도 있다.
            #입력 S의 actCost는 2이다. 
            #그런데.. GameObj의 inputS에 있는 2와 전혀 상관이 없다.        
            # 상관 있게 만들어야 한다.
            if self.gameObj.turnTakerComponent.actCount > 2:
                self.gameObj.inputS()

        elif semanticInput == 'a':
            #이것도 무기 클래스를 만들어야 하겠지.
            self.gameObj.inputA()


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
        self.stateChanger.updateStates()        
        #then: no change
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)
                
    def test_inputSomeKeyToSkipTurnOfPlayer(self):
        #given: 스페이스바로 스킵, 게임 상태를 상태변화자에게 전달
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): 'skip'}
        )
        
        #when: 스페이스바를 누르면(가짜 입력)
        self.pseudoKeyInput(libtcod.KEY_SPACE,' ')
        self.stateChanger.updateStates()
        
        #then: 행동력이 모두 소모됨
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 0)

    def test_inputSomeKeyToMoveGameObj(self):
        #이전 값
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        
        #given: UP key로 위로 1칸 이동
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): 'up'}
        )

        #when: UP key를 누르면
        self.pseudoKeyInput(libtcod.KEY_UP, ihdr.NOT_CHAR)
        self.stateChanger.updateStates()

        #then: 위로 1칸 이동함. 행동력 감소
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY - 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
        

        #given: 다른 게임 오브젝트 움직이기(사실 뻔함)
        ttaker = TurnTaker(5)
        otherPlayer = GameObject(1,2, turnTakerComponent=ttaker)
        self.stateChanger.gameObj = otherPlayer

        #이전 값
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(otherPlayer)
        
        #when: 
        self.pseudoKeyInput(libtcod.KEY_UP, ihdr.NOT_CHAR)        
        self.stateChanger.updateStates()

        #then: 위로 1칸 이동함. 행동력 감소
        self.assertEqualPositionInMap(otherPlayer, beforeX + 0, beforeY - 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
    
    def test_cannotMoveOverObstacle(self):
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): 'down'}
        )

        #변화 이전 값
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        
        #given: userPlayer 한 칸 아래에 장애물 놓기.
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
        obstacleObjRefs.append(
            gameObjFactory.createGameObject( 
                lambda:createObstacle(beforeX, beforeY + 1) 
            )
        )
                   
        #when: DOWN key를 누르면
        self.pseudoKeyInput(libtcod.KEY_DOWN,ihdr.NOT_CHAR)        
        self.stateChanger.updateStates()

        #then: 아래로 1칸 이동 못함. 행동력 감소 안 함. 
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)

    def test_someGameObjCanPenetrateObstacles(self):        
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): 'down'}
        )

        #변화 이전 값
        (beforeX, beforeY) = self.getXYofPlayer(self.userPlayer)

        #given: someObj 한 칸 아래에 장애물 놓기.
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
        obstacleObjRefs.append(
            gameObjFactory.createGameObject( 
                lambda:createObstacle(beforeX, beforeY + 1) 
            )
        )            
        self.userPlayer.canPenetrate = True  #장애물을 관통 가능한 객체.
        
        #when: DOWN key를 두번 누르면 
        self.pseudoKeyInput(libtcod.KEY_DOWN,ihdr.NOT_CHAR)        
        self.stateChanger.updateStates()
        self.stateChanger.updateStates() #두번.

        #then: 객체는 2칸을 내려감.
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY + 2)
       
    def test_noChangeWhenActCostOfDoingIsMoreThanMaxActCountOfPlayer(self):        
        #given: setup시의 maxActCount는 5이고, s를 누르면 행동력 2가 까이는 행동을 함.
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(ihdr.NOT_VK, 's'): 's'}
        )
        #when: 입력이 3번 들어오면 2번까지는 동작하나 마지막은 불가능.
        self.pseudoKeyInput(ihdr.NOT_VK,'s')
                       
        #then: 행동력은 5 -> 's' -> 3 -> 's' -> 1 -> 's' -> 1 이 됨. 
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 3)
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 1)
        self.stateChanger.updateStates() # 3번의 입력, 마지막은 변화 없음.
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 1)

                            
    def test_sameInputToMoveButDifferentActCostEachPlayers(self):
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): 'up'}
        )
        
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: 움직임의 actCost가 2인 플레이어
        ttaker = TurnTaker(5)
        otherPlayer = GameObject(1,2, turnTakerComponent=ttaker, moveCost=2)
        
        self.stateChanger.gameObj = otherPlayer

        #when: 위로 이동
        self.pseudoKeyInput(libtcod.KEY_UP,ihdr.NOT_CHAR)        

        self.stateChanger.updateStates()

        #then: 위로 1칸 이동함. 행동력 2개 감소
        self.assertEqualPositionInMap(otherPlayer, beforeX + 0, beforeY - 1)        
        self.assertActCountConsumptionIsCost(otherPlayer, beforeActCount, cost=2)
    
    def test_sameInputButDifferentAttackIfPlayerHaveWeapon(self):
        #setUp: 'a' 입력 가능
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(ihdr.NOT_VK, 'a'): 'a'}
        )
        
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        #given: weapon 총을 가진 플레이어        
        self.userPlayer.weapon = 'gun'
        #when: 버튼 a를 눌러 공격
        self.pseudoKeyInput(ihdr.NOT_VK,'a')                
        self.stateChanger.updateStates()        
        #then: 총은 공격시에 행동력 2개 쓴다        
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=2)
        
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        #given: weapon 총을 갖지 않은 플레이어
        self.userPlayer.weapon = None
        #when: 버튼 a를 눌러 공격
        self.pseudoKeyInput(ihdr.NOT_VK,'a')        
        self.stateChanger.updateStates()        
        #then: 그냥 공격에 행동력 1개 쓴다
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
            
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
        
        #이전 값
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        # None 입력
        for times in range(10000):
            self.stateChanger.updateStates()
        #입력 결과
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)

        #이전 값
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        # 'a' 입력        
        self.pseudoKeyInput(ihdr.NOT_VK, 's')
        self.stateChanger.updateStates()
        #입력 결과
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=2)

        #이전 값
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        # 'up' 입력
        self.pseudoKeyInput(libtcod.KEY_UP, ihdr.NOT_CHAR)
        self.stateChanger.updateStates()
        #입력 결과
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY - 1)        
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)

    def test_inputButActCountOfPlayerIsZero(self):
        #given: 
        self.stateChanger.setInputTable(
            {ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): 'skip'}
        )                
        #when: 스킵해서 현재 stateChanger의 플레이어 행동력이 0 만들기.
        self.pseudoKeyInput(libtcod.KEY_SPACE,' ')
        self.stateChanger.updateStates()             
        #then: 행동력이 0인데 입력이 들어오는 것은 비정상적인 작동이다.
        self.assertRaises(AssertionError, self.stateChanger.updateStates)

    def test_raiseErrorWhenActCountOfPlayerIsNegativeNumber(self):    
        try:
            self.stateChanger.gameObj.turnTakerComponent.actCount = -1
        except AssertionError:    
            pass
        else:
            self.fail("AssertionError didn't raiesd")
            
######## ai 구현하기 ########
    # ai는 inputHandler의 일종이다. 원시입력 없이 semanticInput을 뽑아낸다...
    # 일단 ai가 판단에 사용하는 상태는 canPenetrate인데... 나중에 게임로직으로 뽑아낼 때 바꿔라.

    def test_ai_MoveGameObjOneCell(self):
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: AI를 stateChanger에 연결
        self.stateChanger.inputHandler = AI(self.userPlayer)
        #when: ai는 userPlayer의 상태(canPenetrate)를 보고 판단하여 위로 한 칸 움직인다!
        self.userPlayer.fakeState = 'up'
        self.stateChanger.updateStates()         
        #then: 위로 한 칸 움직이고 행동력 1 줄이고.                    
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY - 1)        
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
    
    def test_ai_noInputNoStateChange(self):
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: AI를 stateChanger에 연결
        self.stateChanger.inputHandler = AI(self.userPlayer)
        #when: ai는 userPlayer의 상태(fakeState)를 보고 판단하여 이번엔 안 움직인다.
        self.userPlayer.fakeState = None
        self.stateChanger.updateStates()         
        #then: 상태는 변화하지 않는다. 
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)        

    def test_ai_skipTurnOfAI(self):        
        #given: AI를 stateChanger에 연결
        self.stateChanger.inputHandler = AI(self.userPlayer)
        #when: ai는 userPlayer의 상태(fakeState)를 보고 판단- 턴을 skip한다.
        self.userPlayer.fakeState = 'skip'
        self.stateChanger.updateStates()
        #then: 행동력이 모두 소모됨
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 0)

    def test_ai_cannotMoveOverObstacle(self):        
        beforeX = self.userPlayer.x
        beforeY = self.userPlayer.y
        beforeActCount = self.userPlayer.turnTakerComponent.actCount
        self.stateChanger.inputHandler = AI(self.userPlayer)
        #given: userPlayer 한 칸 아래에 장애물 놓기.
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
        obstacleObjRefs.append(
            gameObjFactory.createGameObject( 
                lambda:createObstacle(beforeX, beforeY + 1) 
            )
        )        
        #when: ai는 userPlayer의 상태(fakeState)를 보고 판단-아래로 한 칸 움직이려한다!
        self.userPlayer.fakeState = 'down'
        self.stateChanger.updateStates()         
        #then: 아래로 1칸 이동 못함. 행동력 감소 안 함. 
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)

    def test_ai_noChangeWhenActCostOfSomethingIsMoreThanMaxActCountOfPlayer(self):
        #given: setup시의 maxActCount는 5이고, s를 누르면 행동력 2가 까이는 행동을 함.
        self.stateChanger.inputHandler = AI(self.userPlayer)
        #when: 입력이 3번 들어오면 2번까지는 동작하나 마지막은 불가능.
        self.userPlayer.fakeState = 's'                                
        #then: 행동력은 5 -> 's' -> 3 -> 's' -> 1 -> 's' -> 1 이 됨. 
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 3)
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 1)
        self.stateChanger.updateStates() # 3번의 입력, 마지막은 변화 없음.
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 1)

    def test_ai_inputButActCountOfPlayerIsZero(self):       
        #given: ai 넣기                
        self.stateChanger.inputHandler = AI(self.userPlayer)
        #when: 스킵해서 현재 stateChanger의 플레이어 행동력이 0 만들기.
        self.userPlayer.fakeState = 'skip'              
        self.stateChanger.updateStates()
        #then: 행동력이 0인데 입력이 들어오는 것은 비정상적인 작동이다.
        self.assertRaises(AssertionError, self.stateChanger.updateStates)

    def test_sameStateButDifferentStateChanging(self):
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: 위로만 가는 ai
        self.stateChanger.inputHandler = AI(self.userPlayer, agent='only up')
        #when: ai 입력 한 번
        self.userPlayer.fakeState = 'ai test'
        self.stateChanger.updateStates()
        #then: 한 칸 위로, 행동력 감소
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY - 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
    
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: 아래로만 가는 ai
        self.stateChanger.inputHandler = AI(self.userPlayer, agent='only down')
        #when: ai 입력 한 번
        self.userPlayer.fakeState = 'ai test'
        self.stateChanger.updateStates()
        #then: 한 칸 아래로, 행동력 감소
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY + 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
    
        (beforeX, beforeY) = self.getXYofPlayer(self.userPlayer)
        #given: 스킵하는 ai
        self.stateChanger.inputHandler = AI(self.userPlayer, agent='only skip')
        #when: ai 스킵
        self.userPlayer.fakeState = 'ai test'
        self.stateChanger.updateStates()
        #then: 좌표 변화 없음, 행동력 = 0
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY + 0)
        self.assertEqual(self.userPlayer.turnTakerComponent.actCount, 0)

######## 라운드 로빈 턴 시스템 구현하기 ########
        
    def test_threeAiControllEachPlayersInRoundRobinTurnSystem(self):
        '''
        라운드 로빈 턴 시스템에서 3개의 ai가 각각 하나의 플레이어를 컨트롤 한다.
        '''
        #given: 3개의 ai가 있는 리스트, 3개의 player가 있는 리스트, 턴 시스템.
        
        #when: 턴 시스템 작동
        
        #then: ai들: up only, down only, skip only, 그리고 모두 행동력은 0
        self.assertEqual(playerList[0].turnTakerComponent.actCount, 0)
        self.assertEqual(playerList[1].turnTakerComponent.actCount, 0)
        self.assertEqual(playerList[2].turnTakerComponent.actCount, 0)
        


    @unittest.skip("repeat ai input and state changing")
    def test_rename(self):
        #given: 위로만 가는 AI 
        
        #when-then: 행동력이 0이 될때까지 입력-단언 반복
        pass
                                               
    def pseudoKeyInput(self, vk, c):
        assert type(vk) is int
        assert type(c) is str

        self.key.vk = vk 
        self.key.c = ord(c)

######## 유틸리티 메서드 ########

    def assertEqualPositionInMap(self, gameObj, xInMap, yInMap):
        self.assertEqual(gameObj.x, xInMap, "obj.x :" + str(gameObj.x) + " != " + str(xInMap) + ": expected x")
        self.assertEqual(gameObj.y, yInMap, "obj.y :" + str(gameObj.y) + " != " + str(yInMap) + ": expected y")

    def assertActCountConsumptionIsCost(self, player, beforeActCount, cost):
        self.assertEqual(player.turnTakerComponent.actCount, beforeActCount - cost)

    def getXYofPlayer(self, player):
        return (player.x, player.y)

    def getXYandActCountOfPlayer(self, player):
        return (player.x, player.y, player.turnTakerComponent.actCount)


if __name__ == '__main__':
    unittest.main()
