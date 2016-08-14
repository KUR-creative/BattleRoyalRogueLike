#-*- coding: utf-8 -*-

class InputHandler:
    def __init__(self, key, inputTable):
        '''
        입력에 대한 의존성(key)을 주입하고 입력 테이블(inputTable)을 설정한다.
        inputTable의 key는 libtcod.Key구조체의 속성을 나열한 tuple이다. 
        KeyTuple 유틸 클래스로 쉽게 만들 수 있다.

        :param libtcod.key key: 외부에서 key이벤트를 받는 key구조체에 대한 참조.
        :param dict inputTable: 현재 입력에 대한 반응을 저장
        '''
        self.key = key
        self.inputTable = inputTable

    def inputResult(self):
        '''
        현재 입력에 대한 결과를 반환
        :returns: 입력에 대한 결과가 self.inputTable에 있는 경우 결과 반환, 그렇지 않으면 None 반환
        '''
        try:
            return self.inputTable[KeyInput(self.key)]
        except KeyError:
            return None       

#################### helpers ####################
# 일반적인 경우다. 둘 다 아닌 경우가 있다..
# esc의 경우 vk = 1, c = '\x1b' == chr(27) 이다...
NOT_VK = 65
NOT_CHAR = '\0'

class KeyInput(tuple):
    def __new__(cls,key):
        '''
        libtcod.key를 넣으면 그에 맞는 tuple을 반환한다
        InputHandler.inputTable의 키로 쓸 수 있다. 
        
        libtcod.key -> tuple       

        :param libtcod.key key: tuple로 변환하고 싶은 libtcod.key 구조체 참조
        :returns: key에 맞는 tuple 
        '''
        return tuple.__new__(cls, (key.vk, key.c, 
                                   key.lalt, key.lctrl, 
                                   key.ralt, key.rctrl, 
                                   key.shift) )

class KeyTuple(tuple):
    def __new__(cls, vk, c, 
                lalt=False, lctrl=False, 
                ralt=False, rctrl=False, 
                shift=False):
        '''
        유틸성 클래스. inputTable인 dict를 만들 때
        입력(key)을 정의할 때 유용하다.
            
        parameters -> tuple

        :returns: 입력에 맞는 tuple
        '''
        return tuple.__new__(cls, (vk, ord(c), 
                                   lalt, lctrl, 
                                   ralt, rctrl, 
                                   shift) )
