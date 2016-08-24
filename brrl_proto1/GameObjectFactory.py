class GameObjectFactory:
    '''
    게임오브젝트 생성시 반드시 이 팩토리 클래스를 이용한다.
    이 클래스 생성시 주입된 GameObjectRepository에 새로 생성된 게임오브젝트들이 저장된다.
    makeFunction을 교체해서 다양한 종류의 게임오브젝트를 생성할 수 있다.
    '''
    def __init__(self, gameObjRepository):
        self.gameObjRepository = gameObjRepository

    def createGameObject(self, makeFunction, *weakrefList):
        '''
        게임오브젝트를 생성하고 그걸 가리키는 weak reference를 반환한다.
        생성된 게임오브젝트는 자동으로 가지고 있는 GameObjectRepository에 저장된다.

        반환되는 참조로 게임객체를 자유롭게 이용하거나(예-2차원 배열에 넣는다거나)
        리스트들을 매개변수로 줘서 게임객체들을 리스트들에 자동으로 append할 수도 있다.

        주의: makeFunction은 반드시 게임오브젝트를 생성해야 한다.
        주의: 반환된 약한 참조를 통해 접근한 게임오브젝트는 반드시 임시변수에 저장하라.
             절대로 참조 수를 늘려선 안 된다.

        :param function makeFunction: 게임오브젝트를 생성하는 함수다. 이것을 바꾸면 다른 오브젝트를 생성할 수 있다.
        :param list *weakrefList: 반환값으로 생성하는 약한참조를 따로 저장할 리스트들이다. 

        :returns: type은 weakref.ref; 생성한 게임오브젝트를 GameObjectRepository에 저장하면서 나오는 weak reference를 반환한다.
        '''
        objRef = self.gameObjRepository.add( makeFunction() )
        for wrlist in weakrefList:
            wrlist.append(objRef)
        return objRef;