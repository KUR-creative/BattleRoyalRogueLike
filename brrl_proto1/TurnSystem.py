#-*- coding: utf-8 -*-
import libtcodpy as libtcod

class TurnSystem(object):
    '''
    턴제 로그라이크의 턴제 시스템을 관리한다.
    TODO: 튜플의 리스트로 한번에 받으면서 생성하는 법을 생각하라.

    받은 순서대로 렌더&블릿트한다.
    '''
    def __init__(self, userList, gameObjList, *renderContainer):
        assert len(userList) == len(gameObjList)
        self.userList = userList
        self.gameObjList = gameObjList
        self.renderContainer = renderContainer
        
        self.stateChanger = GameStateChanger(None, None)
        

    def run(self, times=1):       
        '''
        유저와 AI가 순서대로 actCount를 모두 소비할때까지
            a gameObj: (user/ai)입력 -> 상태변화 -> 렌더링
        이 시퀀스를 반복한다.
        ''' 
        for i in range(times):
            for j in range( len(self.gameObjList) ):
                #대상 변경
                self.stateChanger.inputHandler = self.userList[j]
                self.stateChanger.gameObj = self.gameObjList[j]
                #행동력 회복
                self.stateChanger.gameObj.turnTakerComponent.readyToTurnTaking()
                
                #TODO: 마우스이벤트나 gui에 대한 코딩을 하라.
                mouse = libtcod.Mouse() #mouse 이벤트를 받기 전까지만. 임시로.
                #모든 행동력을 소비할 때까지 입력 -> 상태 변화
                while self.stateChanger.gameObj.turnTakerComponent.actCount > 0:
                    # 1.입력
                    nowGameObjIsUserPlayer = self.stateChanger.inputHandler.key
                    if nowGameObjIsUserPlayer:
                        #유저의 입력을 기다림.
                        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,self.stateChanger.inputHandler.key,mouse)
                    
                    # 2.상태변화                                                        
                    messageOutOfTurnSystem = self.stateChanger.updateStates() 
                    
                    # 3. 렌더링            
                    if self._isRenderable(self.gameObjList[j]):                        
                        # ■■■버퍼 지우기■■■
                        libtcod.console_clear(0) 
                        for container in self.renderContainer:
                            container.renderAndBlit()            
                        # ■■■버퍼 비우기■■■
                        libtcod.console_flush() 
            
                    if messageOutOfTurnSystem is not None:
                        return messageOutOfTurnSystem

    def _isRenderable(self, gameObj):
        if(gameObj.renderComponent is not None and
           gameObj.renderComponent.visible is True):
            return True
        else:
            return False


class GameStateChanger(object):
    '''
    입력 받은 게임의 상태에 따라 InputHandler에서 들어온 semanticInput을 
    gameObject의 stateChangerComponent에 따라 상태를 변경한다.

    stateChangerComponent에 대한 인터페이스를 제공한다.

    모든 gameObj에 대한 동일한 상태변화는 여기서 일어날 수도 있다.
    '''
    #DBG: debug = 0
    def __init__(self, inputHandler, gameObj):
        self.gameObj = gameObj
        self.inputHandler = inputHandler

    def setInputTableOfNowUser(self, inputTable):
        '''
        TODO: inputTable이 없는 aiInputHandler는 에러를 낼 것이다.
        예외처리를 해줘야 할까?
        '''
        self.inputHandler.inputTable = inputTable

    def updateStates(self):
        '''
        gameObject의 stateChangerComponent를 이용하여 상태를 바꾼다.
        그래서 플레이어마다 다른 상태 변경을 할 수 있다.
        '''
        assert (self.gameObj.turnTakerComponent.actCount != 0 and 
                "accepted input but player's actCount is 0!")
        
        semanticInput = self.inputHandler.getSemanticInput()
        return self.gameObj.stateChangerComponent.changeState(semanticInput)
