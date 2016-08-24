#-*- coding: utf-8 -*-
'''
오직 유닛 테스트 클래스 Test_game_state_changer만을 위한 모듈.
일종의 게임로직 모듈로써, 이것을 갈아 끼워서 완전히 새로운 게임을 만들 수 있다.
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import utilities as util

semanticInputs = util.enum('UP', 'DOWN', 'SKIP', 'KEY_S', 'KEY_A', 'ESC')

def isObstacleAt(xInMap, yInMap, obstacleObjRefs):
    '''
    입력된 좌표에서 장애물이 있는가?

    :param int xInMap: 알고 싶은 맵의 x좌표
    :param int yInMap: 알고 싶은 맵의 y좌표
    :param weakref obstacleObjRefs: 장애물 약한참조가 있는 리스트

    :returns: Obstacle이 있으면 True / 없으면 False
    '''
    for obstacleRef in obstacleObjRefs:
        if(obstacleRef().x == xInMap and 
           obstacleRef().y == yInMap):
            return True
    return False

class testStateChangerCompo:
    '''
    덕타이핑을 써서, 아래 함수만 있으면 어떤 클래스든 이게 될 수 있다.
    또 이거는 gameObject에 들어가는 컴포넌트이므로 얼마든지 gobj(owner)에 접근 가능.
    '''

    def __init__(self, obstacleObjRefs):
        assert type(obstacleObjRefs) is list
        self.obstacleObjRefs = obstacleObjRefs

    def changeState(self, semanticInput):
        if semanticInput is None: 
            return None

        elif semanticInput == semanticInputs.SKIP: 
            self.owner.skip()
                    
        elif semanticInput == semanticInputs.UP:
            self.owner.move(0, -1)
        
        elif semanticInput == semanticInputs.DOWN:
            if(isObstacleAt(self.owner.x + 0, self.owner.y + 1, self.obstacleObjRefs) and 
               not self.owner.canPenetrate ):
                print "cannot move over blocked obstacle!"  
            else:
                self.owner.move(0, +1)
        
        elif semanticInput == semanticInputs.KEY_S: 
            if self.owner.turnTakerCompo.actCount > 2:
                self.owner.inputS()

        elif semanticInput == semanticInputs.KEY_A:
            #이것도 무기 클래스를 만들어야 하겠지.
            self.owner.inputA()

        elif semanticInput == semanticInputs.ESC:
            return 'exit' #
        
        if(self.owner.fighterCompo is not None and
           self.owner.fighterCompo.hp == 0 and
           self.owner.fighterCompo.isTemporary):
            return 'user is dead'

        print semanticInput, #DBG       
        
            
################ ai agents ################ 
class testOnlyUpAi(object):
    def calcNextAct(self, nowGameState):
        return semanticInputs.UP

class testOnlyDownAi(object):
    def calcNextAct(self, nowGameState):
        return semanticInputs.DOWN

class testOnlySkipAi(object):
    def calcNextAct(self, nowGameState):
        return semanticInputs.SKIP

class testMultiAi(object):
    def __init__(self):
        self._innerFlag = 0
    def calcNextAct(self, nowGameState):
        if self._innerFlag == 0:
            self._innerFlag += 1
            return semanticInputs.UP
        else:
            return semanticInputs.SKIP

class testSKeyAi(object):
    def calcNextAct(self, nowGameState):
        return semanticInputs.KEY_S