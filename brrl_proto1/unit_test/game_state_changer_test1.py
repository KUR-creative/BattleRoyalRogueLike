#-*- coding: utf-8 -*-
'''
이 모듈의 테스트들은 모두 구체적이고 암묵적인 [값]에 의존하고 있다.
회귀테스트에서 쓰려면 그래서는 안 된다. 
지금까지 테스트에 쓰인 모든 [값]들을 어딘가에 모아두어야 한다.
또 게임 로직은 매우 쉽게 변하는 부분인데, 
GameStateChanger와 GameObject에 퍼져서 있다.
이 로직을 분리해야 한다...

현재 GameObject는 fake객체이다. 이거는 이 테스트 모듈 내에서만 쓰일 수 있다.
테스트에서만 쓰일 법한 부분을 게임 로직으로 분리해 내라.


'''

import unittest
import libtcodpy as libtcod
import weakref

from unit_test import game_logic_for_game_state_changer as test_game

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import GameObjectFactory as gfac
from brrl_proto1 import GameObjectRepository as grepo
from brrl_proto1 import TurnSystem as tsys

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import input_handler as ihdr


######## gameObject and components ########
# 게임 객체와 컴포넌트들은 아직 모듈로 분리하기에는 완전히 리팩토링되지 않았다.
class GameObject(object):
    '''
    테스트용 페이크 객체인가?

    게임 객체에 대한 정보를 담는다.
    게임 객체 자체의 상태만을 변경하는 메서드가 있다.
    외부(obstacle 등..)에 대해 알지 못한다.

    예)외부 상태에 의존적인 행위(움직임/근접공격)는 정의할 수 없다. 
    근처에 장애물이 있는지 게임 객체 혼자서는 알 수가 없거든
    그런 건 stateChangerComponent에게 책임을 넘긴다.
    '''
    def __init__(self, xInMap, yInMap, 
                 renderComponent=None, 
                 obstacleComponent=None, 
                 fighterComponent=None,
                 turnTakerComponent=None,
                 stateChangerComponent=None,
                 canPenetrate=False,
                 moveCost=1):
        self.x = xInMap
        self.y = yInMap
        self.canPenetrate = canPenetrate        
        self.moveCost = moveCost  
        
        #리스트에 컴포넌트들을 집어넣고 enum을 만드는 식으로 리팩토링 가능하지만...글쎄..
        self.renderCompo = self.setOwnerOf(renderComponent)
        self.obstacleCompo = self.setOwnerOf(obstacleComponent)        
        self.fighterCompo = self.setOwnerOf(fighterComponent)
        self.turnTakerCompo = self.setOwnerOf(turnTakerComponent)
        self.stateChangerCompo = self.setOwnerOf(stateChangerComponent)

    def setOwnerOf(self, component):
        if component is not None:
            component.owner = self
        return component
            
    # 게임 오브젝트는 할 수 있는 일들이 종류마다 다들 다르다.
    # 메서드로 하기에는 좀... 메서드는 너무 정적이다. 이걸 어떻게 리팩토링하는가?
    # TODO: need refactoring
    def move(self, dx, dy):   
        #행동력을 뺄 수 있을 때만 움직일 수 있다.
        self.turnTakerCompo.actCount -= self.moveCost # 이 값은 어떻게 리팩토링하지?

        self.x += dx
        self.y += dy               

        if self.renderCompo is not None:
            self.renderCompo.x += dx
            self.renderCompo.y += dy
                    
    
    def skip(self):
        self.turnTakerCompo.actCount = 0

    #위에 것들은 당연하고 지켜야 한다. 아래 것들은 그렇지 않다.
    #아예 키 매핑을 해주는 메서드를 만드는 것도 고려해보자.
    def inputS(self):
        self.turnTakerCompo.actCount -= 2

    def inputA(self):
        if self.weapon == 'gun':
            self.turnTakerCompo.actCount -= 2
        else:
            self.turnTakerCompo.actCount -= 1
                
    #TODO:리팩토링 필요.    
    def getAvailableStates(self):
        '''
        게임오브젝트 사용자(유저/AI)에게 전달하는 게임오브젝트의 상태들
        이후 실제 게임에서 전달될 변수들이 결정되며 이걸 기준으로 렌더링도 함.
        전달용 클래스가 있어야 할지도 몰라.
        이후에 GameObject를 새로 작성할 때 반드시 바뀌어야 한다.
        '''
        pass        
'''
class Obstacle(object):
    def __init__(self, obstacleRefs, blocked=False):      
        self.obstacleRefs = obstacleRefs
        self._blocked = blocked

    @property
    def blocked(self):
        return self._blocked

    @blocked.setter
    def blocked(self, bool):
        self._blocked = bool
        if bool is True:
            self.obstacleRefs.append(weakref.ref(self.owner))#이거도 겹치는 거 아닌가?
        else:
            self.obstacleRefs = []
            self.obstacleRefs.remove(
'''
#리팩토링을 위한 테스트 코드를 써라.

class Obstacle(object):
    def __init__(self, blocked=False):      
        self.blocked = blocked

def createObstacle(x, y):
    mCompo = Obstacle(True)
    return GameObject(x, y, obstacleComponent=mCompo)

class TurnTaker(object):
    '''
    이 클래스에서 턴이 0이 된 이후에 일어나는 일을 정의 할 수도 있다.
    #그리고 TurnSystem에서 호출하면 된다.
    '''
    def __init__(self, maxActCount):
        self.maxActCount = maxActCount        
        self._actCount = maxActCount

    @property
    def actCount(self):
        return self._actCount

    @actCount.setter
    def actCount(self, val):        
        assert (val >= 0 and "player's actCount is negative number. FATAL error!")
        self._actCount = val

    def readyToTurnTaking(self):
        '''
        턴 시작을 위한 준비 - 행동력 회복.
        '''
        self.actCount = self.maxActCount
        if self.owner.fighterCompo is not None:
            self.owner.fighterCompo.hpSubtraction()

class Fighter(object):
    def __init__(self, hp, power=0, corpseChar=u'死', isTemporary=False):
        self._hp = hp
        self.power = power
        self.corpseChar = corpseChar
        self.isTemporary = isTemporary

        self.attackCost = 1
        
    def attack(self, targetFighter):
        print targetFighter.hp, ' - ', #DBG

        self.owner.turnTakerCompo.actCount -= self.attackCost # 이 값은 어떻게 리팩토링하지?
        targetFighter.hp -= self.power

        print self.power, ' = ', targetFighter.hp, ':target hp' #DBG

    def die(self):
        #dead player is not Obstacle
        self.owner.obstacleCompo.blocked = False
        #dead player can't act
        tCompo = self.owner.turnTakerCompo
        if tCompo is not None:
            tCompo.actCount = 0
            tCompo.maxActCount = 0
        #dead player left corpse
        rCompo = self.owner.renderCompo
        if rCompo is not None:
            rCompo.char = self.corpseChar

        print 'he is dead!' #DBG

    def hpSubtraction(self):
        if self.isTemporary:
            self.hp -= 1           

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, val):
        self._hp = val
        if self._hp < 0:
            self.die()
    


semanticInputs = test_game.semanticInputs

obstacleObjRefs = []

######## test cases ########
class Test_game_state_changer(unittest.TestCase):
    def setUp(self):
        self.key = libtcod.Key()
        
        self.initMaxActCount = 5
        ttaker = TurnTaker(self.initMaxActCount)
        self.userPlayer = GameObject(1,2, turnTakerComponent=ttaker,
                                     stateChangerComponent=test_game.testStateChangerCompo(obstacleObjRefs))
        
        #원시입력핸들러와 게임상태변경자 연결
        testInputTable = dict()        
        ihandler = ihdr.InputHandler(self.key, testInputTable)        
        self.stateChanger = tsys.GameStateChanger(ihandler, self.userPlayer)
       
        return super(Test_game_state_changer, self).setUp()

    def tearDown(self):
        #clear obstacles.
        del obstacleObjRefs[:]

        return super(Test_game_state_changer, self).tearDown()
    
    def test_noInputNoStateChange(self):                            
        #given: no available input(default inputTable in setUp())        
        #when: no input 
        beforeActCount = self.userPlayer.turnTakerCompo.actCount
        self.stateChanger.updateStates()        
        #then: no change
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)
                
    def test_inputSomeKeyToSkipTurnOfPlayer(self):
        #given: 스페이스바로 스킵, 게임 상태를 상태변화자에게 전달
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): semanticInputs.SKIP}
        )
        
        #when: 스페이스바를 누르면(가짜 입력)
        self.pseudoKeyInput(libtcod.KEY_SPACE,' ')
        self.stateChanger.updateStates()
        
        #then: 행동력이 모두 소모됨
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 0)

    def test_inputSomeKeyToMoveGameObj(self):
        #이전 값
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        
        #given: UP key로 위로 1칸 이동
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): semanticInputs.UP}
        )

        #when: UP key를 누르면
        self.pseudoKeyInput(libtcod.KEY_UP, ihdr.NOT_CHAR)
        self.stateChanger.updateStates()

        #then: 위로 1칸 이동함. 행동력 감소
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY - 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
        

        #given: 다른 게임 오브젝트 움직이기(사실 뻔함)
        ttaker = TurnTaker(5)
        otherPlayer = GameObject(1,2, turnTakerComponent=ttaker,
                                 stateChangerComponent=test_game.testStateChangerCompo(obstacleObjRefs))
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
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): semanticInputs.DOWN}
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
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(libtcod.KEY_DOWN, ihdr.NOT_CHAR): semanticInputs.DOWN}
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
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(ihdr.NOT_VK, 's'): semanticInputs.KEY_S}
        )
        #when: 입력이 3번 들어오면 2번까지는 동작하나 마지막은 불가능.
        self.pseudoKeyInput(ihdr.NOT_VK,'s')
                       
        #then: 행동력은 5 -> 's' -> 3 -> 's' -> 1 -> 's' -> 1 이 됨. 
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 3)
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 1)
        self.stateChanger.updateStates() # 3번의 입력, 마지막은 변화 없음.
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 1)

                            
    def test_sameInputToMoveButDifferentActCostEachPlayers(self):
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): semanticInputs.UP}
        )
        
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: 움직임의 actCost가 2인 플레이어
        ttaker = TurnTaker(5)
        otherPlayer = GameObject(1,2, turnTakerComponent=ttaker, 
                                 moveCost=2,
                                 stateChangerComponent=test_game.testStateChangerCompo(obstacleObjRefs))
        
        self.stateChanger.gameObj = otherPlayer

        #when: 위로 이동
        self.pseudoKeyInput(libtcod.KEY_UP,ihdr.NOT_CHAR)        

        self.stateChanger.updateStates()

        #then: 위로 1칸 이동함. 행동력 2개 감소
        self.assertEqualPositionInMap(otherPlayer, beforeX + 0, beforeY - 1)        
        self.assertActCountConsumptionIsCost(otherPlayer, beforeActCount, cost=2)
    
    def test_sameInputButDifferentAttackIfPlayerHaveWeapon(self):
        #setUp: 'a' 입력 가능
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(ihdr.NOT_VK, 'a'): semanticInputs.KEY_A}
        )
        
        beforeActCount = self.userPlayer.turnTakerCompo.actCount
        #given: weapon 총을 가진 플레이어        
        self.userPlayer.weapon = 'gun'
        #when: 버튼 a를 눌러 공격
        self.pseudoKeyInput(ihdr.NOT_VK,'a')                
        self.stateChanger.updateStates()        
        #then: 총은 공격시에 행동력 2개 쓴다        
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=2)
        
        beforeActCount = self.userPlayer.turnTakerCompo.actCount
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
        self.stateChanger.setInputTableOfNowUser(            
             {ihdr.KeyTuple(ihdr.NOT_VK, 's'): semanticInputs.KEY_S,
              ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR): semanticInputs.UP,
              ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): semanticInputs.SKIP}
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
        self.stateChanger.setInputTableOfNowUser(
            {ihdr.KeyTuple(libtcod.KEY_SPACE, ' '): semanticInputs.SKIP}
        )                
        #when: 스킵해서 현재 stateChanger의 플레이어 행동력이 0 만들기.
        self.pseudoKeyInput(libtcod.KEY_SPACE,' ')
        self.stateChanger.updateStates()             
        #then: 행동력이 0인데 입력이 들어오는 것은 비정상적인 작동이다.
        self.assertRaises(AssertionError, self.stateChanger.updateStates)

    def test_raiseErrorWhenActCountOfPlayerIsNegativeNumber(self):    
        try:
            self.stateChanger.gameObj.turnTakerCompo.actCount = -1
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
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testOnlyUpAi())
        #when: ai는 그냥 한 칸 움직인다!
        self.stateChanger.updateStates()         
        #then: 위로 한 칸 움직이고 행동력 1 줄이고.                    
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY - 1)        
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
        
    
    @unittest.skip("TODO: refactoring. '인풋이 없으면 변화도 없다'는 테스트는 필요하지만, 지금 방식으론 테스트가 불가능하다.")
    def test_ai_noInputNoStateChange(self):
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: AI를 stateChanger에 연결
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.test_onlyUpAi())
        #when: ai는 안 움직인다.
        self.stateChanger.updateStates()         
        #then: 상태는 변화하지 않는다. 
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)        
                
    def test_ai_skipTurnOfAI(self):        
        #given: AI를 stateChanger에 연결
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testOnlySkipAi())
        #when: ai는 턴을 skip한다.
        self.stateChanger.updateStates()
        #then: 행동력이 모두 소모됨
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 0)
       
    def test_ai_cannotMoveOverObstacle(self):        
        beforeX = self.userPlayer.x
        beforeY = self.userPlayer.y
        beforeActCount = self.userPlayer.turnTakerCompo.actCount
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testOnlyDownAi())
        #given: userPlayer 한 칸 아래에 장애물 놓기.
        gameObjFactory = gfac.GameObjectFactory(grepo.GameObjectRepository())
        obstacleObjRefs.append(
            gameObjFactory.createGameObject( 
                lambda:createObstacle(beforeX, beforeY + 1) 
            )
        )        
        #when: ai는 아래로 한 칸 움직이려한다!
        self.stateChanger.updateStates()         
        #then: 아래로 1칸 이동 못함. 행동력 감소 안 함. 
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=0)
        self.assertEqualPositionInMap(self.userPlayer, beforeX, beforeY)
            
    def test_ai_noChangeWhenActCostOfSomethingIsMoreThanMaxActCountOfPlayer(self):
        #given: setup시의 maxActCount는 5이고, s를 누르면 행동력 2가 까이는 행동을 함.
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testSKeyAi())
        #when: 입력이 3번 들어오면 2번까지는 동작하나 마지막은 불가능.
        #then: 행동력은 5 -> 's' -> 3 -> 's' -> 1 -> 's' -> 1 이 됨. 
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 3)
        self.stateChanger.updateStates() 
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 1)
        self.stateChanger.updateStates() # 3번의 입력, 마지막은 변화 없음.
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 1)
    
    def test_ai_inputButActCountOfPlayerIsZero(self):       
        #given: ai 넣기                
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testOnlySkipAi())
        #when: 스킵해서 현재 stateChanger의 플레이어 행동력이 0 만들기.
        self.stateChanger.updateStates()
        #then: 행동력이 0인데 입력이 들어오는 것은 비정상적인 작동이다.
        self.assertRaises(AssertionError, self.stateChanger.updateStates)
    
    def test_ai_sameStateButDifferentStateChanging(self):
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: 위로만 가는 ai
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testOnlyUpAi())
        #when: ai 입력 한 번
        self.stateChanger.updateStates()
        #then: 한 칸 위로, 행동력 감소
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY - 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
        
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: 아래로만 가는 ai
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testOnlyDownAi())
        #when: ai 입력 한 번        
        self.stateChanger.updateStates()
        #then: 한 칸 아래로, 행동력 감소
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY + 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
    
        (beforeX, beforeY) = self.getXYofPlayer(self.userPlayer)
        #given: 스킵하는 ai
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testOnlySkipAi())
        #when: ai 스킵        
        self.stateChanger.updateStates()
        #then: 좌표 변화 없음, 행동력 = 0
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY + 0)
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 0)
    
    def test_ai_multiActPatternAI(self):
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        #given: 전략을 수정하는 ai
        self.stateChanger.inputHandler = ihdr.AiInputHandler(self.userPlayer, test_game.testMultiAi())
        # 1. go up
        self.stateChanger.updateStates() 
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY - 1)
        self.assertActCountConsumptionIsCost(self.userPlayer, beforeActCount, cost=1)
        # 2. skip
        (beforeX, beforeY, beforeActCount) = self.getXYandActCountOfPlayer(self.userPlayer)
        self.stateChanger.updateStates()
        self.assertEqualPositionInMap(self.userPlayer, beforeX + 0, beforeY + 0)
        self.assertEqual(self.userPlayer.turnTakerCompo.actCount, 0)
        
    def test_raiseErrorWhenTurnSystemCannotMakePairOfUsersAndGameObjects(self):
        ulist = [1,2,3]
        glist = [1,2]
        self.assertRaises(AssertionError, lambda:tsys.TurnSystem(ulist,glist))

######## 라운드 로빈 턴 시스템 구현하기(실제루프 사용) ########        
    def test_threeAiControllEachPlayersInRoundRobinTurnSystem(self):
        '''
        라운드 로빈 턴 시스템에서 3개의 ai가 각각 하나의 플레이어를 컨트롤 한다.
        나중에 n개의 플레이어에 대해 테스트 할 수 있고,
        이후 게임 로직이 분리된다면 그것을 이용하여 단언 코드도 작성할 수 있을 것이다.
        '''
        #given:
        # 3개의 player가 있는 리스트
        playerList = []                
        for i in range(3):
            ttaker = TurnTaker(self.initMaxActCount)
            player = GameObject(i*10, i*10, 
                                turnTakerComponent=ttaker,
                                stateChangerComponent=test_game.testStateChangerCompo(obstacleObjRefs))
            playerList.append(player)
        # 3개의 ai가 있는 리스트
        aiList = [ihdr.AiInputHandler(playerList[0], test_game.testOnlyUpAi()),
                  ihdr.AiInputHandler(playerList[1], test_game.testOnlyDownAi()),
                  ihdr.AiInputHandler(playerList[2], test_game.testOnlySkipAi())]        
        # 3개의 유저 상태가 있는 리스트
        x = 0; y = 1; ac = 2; #actCount
        beforeTuples = [self.getXYandActCountOfPlayer(playerList[i]) for i in range(3)]
        
        #when: 턴 시스템 작동
        turnSystem = tsys.TurnSystem(aiList, playerList)
        turnSystem.run(1) #루프 한번 
        
        #then: ai들: up only, down only, skip only, 그리고 
        #모두 행동력은 0 - 즉 행동력 5를 모두 소비함.
        self.assertEqual(playerList[0].turnTakerCompo.actCount, 0)
        self.assertEqual(playerList[1].turnTakerCompo.actCount, 0)
        self.assertEqual(playerList[2].turnTakerCompo.actCount, 0)
        
        self.assertEqualPositionInMap(playerList[0], beforeTuples[0][x], beforeTuples[0][y] - 5) #up
        self.assertEqualPositionInMap(playerList[1], beforeTuples[1][x], beforeTuples[1][y] + 5) #down
        self.assertEqualPositionInMap(playerList[2], beforeTuples[2][x], beforeTuples[2][y] + 0) #skip

        #given: 다시 현재 상태 저장
        beforeTuples = [self.getXYandActCountOfPlayer(playerList[i]) for i in range(3)]
        #when: 루프 n번
        n = 7
        turnSystem.run(n)
        #then: ai들: up only, down only, skip only, 그리고 
        #모두 행동력은 0 - 즉 행동력 5를 모두 소비함.        
        self.assertEqualPositionInMap(playerList[0], beforeTuples[0][x], beforeTuples[0][y] - 5*n) #up
        self.assertEqualPositionInMap(playerList[1], beforeTuples[1][x], beforeTuples[1][y] + 5*n) #down
        self.assertEqualPositionInMap(playerList[2], beforeTuples[2][x], beforeTuples[2][y] + 0) #skip
    
    def test_manual_userPlayerInTurnSystemInRunningGameLoop(self):
        print "\n manual test:"
        print " press ESC key to end test."
        
        #given:
        # 3+1개의 player가 있는 리스트
        playerList = []                        
        for i in range(3):
            ttaker = TurnTaker(self.initMaxActCount)
            player = GameObject(i*10, i*10, 
                                turnTakerComponent=ttaker,
                                stateChangerComponent=test_game.testStateChangerCompo(obstacleObjRefs))
            playerList.append(player)       #ai
        playerList.append(self.userPlayer)  #user

        # 3개의 ai + 유저가 있는 리스트
        aiList = [ihdr.AiInputHandler(playerList[0], test_game.testOnlyUpAi()),
                  ihdr.AiInputHandler(playerList[1], test_game.testOnlyDownAi()),
                  ihdr.AiInputHandler(playerList[2], test_game.testOnlySkipAi()),
                  ihdr.InputHandler(self.key, {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):semanticInputs.UP,
                                               ihdr.KeyTuple(libtcod.KEY_ESCAPE, '\x1b'):   semanticInputs.ESC}) ]        
        
        # 3+1개의 플레이어 상태가 있는 리스트
        x = 0; y = 1; ac = 2; #actCount
        beforeTuples = [self.getXYandActCountOfPlayer(playerList[i]) for i in range(4)]
        
        loop = 1
        self.initLibtcodWindow()
        turnSystem = tsys.TurnSystem(aiList, playerList)
        while not libtcod.console_is_window_closed():                      
            mouse = libtcod.Mouse()
            
            #when: 턴 시스템 작동            
            exit = turnSystem.run() #루프 한번         
                    
            #유저의 esc 입력으로 테스트 종료 가능.
            if exit == 'exit':
                break

            #then: ai들: up only, down only, skip only, 그리고 유저. 
            #모두 행동력은 0 - 즉 행동력 5를 모두 소비함.
            self.assertEqual(playerList[0].turnTakerCompo.actCount, 0)
            self.assertEqual(playerList[1].turnTakerCompo.actCount, 0)
            self.assertEqual(playerList[2].turnTakerCompo.actCount, 0)
            self.assertEqual(playerList[2].turnTakerCompo.actCount, 0)
        
            self.assertEqualPositionInMap(playerList[0], beforeTuples[0][x], beforeTuples[0][y] - 5*loop) #up
            self.assertEqualPositionInMap(playerList[1], beforeTuples[1][x], beforeTuples[1][y] + 5*loop) #down
            self.assertEqualPositionInMap(playerList[2], beforeTuples[2][x], beforeTuples[2][y] + 0*loop) #skip
            self.assertEqualPositionInMap(playerList[3], beforeTuples[3][x], beforeTuples[3][y] - 5*loop) #user input 'up'

            loop += 1

    @unittest.skip("거 좀만 하지 말자. proto1 다 만들 때까지만 참으쇼 쫌")
    def test_manual_stopRunningTurnSystemWhenUserIsDead(self):
        print "\n manual test:"
        print " user will be dead in 3 turns"
        
        #given:
        initHp = 3
        self.userPlayer.fighterCompo = Fighter(initHp, isTemporary=True)
        
        #num = 4
        # 3+1개의 player가 있는 리스트
        playerList = []                        
        for i in range(3):
            ttaker = TurnTaker(self.initMaxActCount)
            player = GameObject(i*10, i*10, turnTakerComponent=ttaker, 
                                            fighterComponent=Fighter(initHp),
                                            stateChangerComponent=test_game.testStateChangerCompo(obstacleObjRefs))
            playerList.append(player)       #ai
        playerList.append(self.userPlayer)  #user

        # 3개의 ai + 유저가 있는 리스트
        aiList = [ihdr.AiInputHandler(playerList[0], test_game.testOnlyUpAi()),
                  ihdr.AiInputHandler(playerList[1], test_game.testOnlyDownAi()),
                  ihdr.AiInputHandler(playerList[2], test_game.testOnlySkipAi()),
                  ihdr.InputHandler(self.key, {ihdr.KeyTuple(libtcod.KEY_UP, ihdr.NOT_CHAR):semanticInputs.UP}) ]        
        
        loop = 1
        self.initLibtcodWindow()
        turnSystem = tsys.TurnSystem(aiList, playerList)
        while not libtcod.console_is_window_closed():                      
            mouse = libtcod.Mouse()
            
            #when: 턴 시스템 작동            
            flag = turnSystem.run() #루프 한번         
                
            #then: ai들: up only, down only, skip only, 그리고 유저. 
            #유저는 hp가 1턴에 1씩 줄어들게 됨. ai는 멀쩡함.
            self.assertEqual(playerList[1].fighterCompo.hp, initHp)           
            self.assertEqual(self.userPlayer.fighterCompo.hp, initHp - loop)           
            
            #유저가 죽으면 게임 종료.
            if self.userPlayer.fighterCompo.hp == 0:
                #원래 게임 루프는 이걸 알면 안됨..
                self.assertEqual(flag, 'user is dead')
                print '\n >>> user is dead!!'
                break
            
            loop += 1

######## 테스트 유틸리티 메서드 ########
    def assertEqualPositionInMap(self, gameObj, xInMap, yInMap):
        self.assertEqual(gameObj.x, xInMap, "obj.x :" + str(gameObj.x) + " != " + str(xInMap) + ": expected x")
        self.assertEqual(gameObj.y, yInMap, "obj.y :" + str(gameObj.y) + " != " + str(yInMap) + ": expected y")

    def assertActCountConsumptionIsCost(self, player, beforeActCount, cost):
        self.assertEqual(player.turnTakerCompo.actCount, beforeActCount - cost)

    def pseudoKeyInput(self, vk, c):
        assert type(vk) is int
        assert type(c) is str

        self.key.vk = vk 
        self.key.c = ord(c)

    def getXYofPlayer(self, player):
        return (player.x, player.y)

    def getXYandActCountOfPlayer(self, player):
        return (player.x, player.y, player.turnTakerCompo.actCount)

    def initLibtcodWindow(self):
        libtcod.console_set_custom_font( 'font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        libtcod.console_init_root(30, 30, 'python + libtcod tutorial', False)
        libtcod.sys_set_fps(20)


if __name__ == '__main__':
    unittest.main()
