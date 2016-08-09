#-*- coding: utf-8 -*-
import weakref


class GameObjectRepository(object):
    '''
    게임에 등장하는 모든 GameObject를 저장한다.
    모든 GameObject는 생성시 반드시 여기 저장되어야한다.
    이 저장소를 clear하면 게임에 사용되는 GameObject들의 메모리를 초기화할 수 있다.
    '''
    def __init__(self):
        self._gameObjSet = set()
        self._numGameObj = 0        

    def add(self, gameObj):
        '''
        gameObj를 내부 set에 저장과 동시에 
        저장한 GameObject의 weak reference를 반환한다.

        중복되는 게임오브젝트를 add할 경우 동일한 약한참조가 반환된다.

        주의: 반환된 약한 참조를 통해 접근한 게임오브젝트를 지역변수가 아닌 변수에 대입하지 마시오.
        (set에 저장된 GameObj들의 참조 카운터를 의도치 않게 늘리지 마시오)

        :param GameObject gameObj: 저장할 게임 오브젝트
        :returns: 저장하는 게임 오브젝트를 가리키는 weakref
        '''
        self._gameObjSet.add(gameObj)
        self._numGameObj += 1        
        return weakref.ref(gameObj)

    def remove(self, gameObjWeakRef):
        '''
        repository의 원소 하나를 삭제한다. 반드시 원소에 대한 weakref를 알아야 한다.
        
        주의:존재하지 않는 원소를 삭제하려하면 KeyError가 raise된다.
        주의: weakref.ref가 아닌 타입이 들어오면 AssertionError raise

        :param weakref.ref gameObjWeakRef: 삭제하려는 원소를 가리키는 약한 참조
        '''
        assert type(gameObjWeakRef) is weakref.ref

        self._gameObjSet.remove(gameObjWeakRef())
        self._numGameObj -= 1

    '''
    TODO: remove 변경 제안
    remove(self, gameObjWeakRef, weakRefList):
        이제 weakRefList를 재귀적으로 검색해서 
        gameObjWeakRef와 동일한 weakref들을 삭제할 수 있다.

        모든 weakreflist에 대해 gameObjWeakRef를 지우고 싶다면
        weakRefList = [tileRefs, obstacleObjRefs, .... ,모든 약한참조 리스트] 이렇게 넣으면 되고
        특정 약한참조 리스트만 넣어서 성능을 올릴수도 있다.

        이 방식을 통해서 None이 된 객체를 참조하는 일이 일어나지 않게 할 수 있다.

        그러나 변경은 나중에 게임오브젝트를 삭제해야하는 부분에서 한다.
        tdd로. 그 때에는 또 조건이 달라질수도 있다.
    '''


    def clear(self):
        '''
        repository에 있는 모든 원소를 삭제한다.
        원래 비어 있다면 아무 일도 일어나지 않는다.
        '''
        self._gameObjSet.clear()
        self._numGameObj = 0

    @property
    def numGameObj(self):
        return self._numGameObj

