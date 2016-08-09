class GameObjectFactory:
    '''
    게임오브젝트 생성시 반드시 이 팩토리 클래스를 이용한다.
    이 클래스 생성시 주입된 GameObjectRepository에 새로 생성된 게임오브젝트들이 저장된다.
    makeFunction을 교체해서 다양한 종류의 게임오브젝트를 생성할 수 있다.
    '''
    def __init__(self, gameObjRepository):
        self.gameObjRepository = gameObjRepository

    def createGameObject(self, makeFunction):
        '''
        게임오브젝트를 생성하고 그걸 가리키는 weak reference를 반환한다.
        생성된 게임오브젝트는 자동으로 가지고 있는 GameObjectRepository에 저장된다.

        주의: makeFunction은 반드시 게임오브젝트를 생성해야 한다.

        :param function makeFunction: 게임오브젝트를 생성하는 함수다. 이것을 바꾸면 다른 오브젝트를 생성할 수 있다.
        :returns: type은 weakref.ref; 생성한 게임오브젝트를 GameObjectRepository에 저장하면서 나오는 weak reference를 반환한다.
        '''
        objRef = self.gameObjRepository.add( makeFunction() )
        return objRef;