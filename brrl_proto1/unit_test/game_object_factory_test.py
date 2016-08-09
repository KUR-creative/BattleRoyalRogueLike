#-*- coding: utf-8 -*-
import unittest

# import GameObjectRepository
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import GameObjectRepository as grepo

# import GameObjectFactory
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import GameObjectFactory as gfac

#for test only
class GameObject:
    def __init__(self, xInMap, yInMap, 
                 renderComponent=None, 
                 obstacleComponent=None, 
                 fighterComponent=None):
        self.xInMap = xInMap
        self.yInMap = yInMap


class Test_GameObjectFactory(unittest.TestCase):
    def setUp(self):
        self.repository = grepo.GameObjectRepository()
        self.factory = gfac.GameObjectFactory(self.repository)        
        
    def test_createGameObjWithoutMakeFunction(self):
        self.assertRaises(TypeError, self.factory.createGameObject, None)

    def test_createSomeGameObject(self):
        gameObjRef = self.factory.createGameObject(self.makeFunc)
        #정말로 weakref가 나오는가? (사실 이것은 연결된 GameObjectRepository을 테스트한다)
        self.assertEqual( type(gameObjRef()), type(GameObject(3,4)), "maybe gameObjRef is not weakref type.")

    def test_depositGameObjRepositoryWhenCreating(self):
        before = self.repository.numGameObj        
        gameObjRef = self.factory.createGameObject(self.makeFunc)
        #저장소에 저장된 수가 늘어났는가?
        self.assertEqual(self.repository.numGameObj, before+1, "cannot add the obj to repository")
        #진짜 들어갔는가?
        self.assertEqual(gameObjRef().xInMap, self.makeFunc().xInMap)

    def test_changeMakeFunction(self):
        originFuncRef = self.factory.createGameObject(self.makeFunc)
        otherFuncRef = self.factory.createGameObject(self.otherMakeFunc)
        #makeFunction을 바꿔서 다양한 오브젝트를 만들 수 있는가?
        self.assertNotEqual(originFuncRef().xInMap, otherFuncRef().xInMap, "function changing did't work or same function argument passed to create two reference")

    def makeFunc(self):
        return GameObject(1,2)
    def otherMakeFunc(self):
        return GameObject(10,20)


if __name__ == '__main__':
    unittest.main()
