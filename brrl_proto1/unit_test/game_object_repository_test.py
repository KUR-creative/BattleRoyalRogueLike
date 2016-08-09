#-*- coding: utf-8 -*-
import unittest
import sys

# import GameObjectRepository
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import GameObjectRepository as grepo

class GameObject:
    pass

class Test_GameObjectRepository(unittest.TestCase):
    def setUp(self):
        self.repo = grepo.GameObjectRepository()

        # 1개 추가!
        gobj = GameObject()
        self.gobjwref = self.repo.add(gobj)
        self.assertEqual(self.gobjwref(), gobj)

        self.assertEqual(self.repo.numGameObj, 1)

    def test_addGameObject(self):
        # 2번째 추가!
        gobj2 = GameObject()
        self.wref = self.repo.add(gobj2)
        self.assertEqual(self.wref(), gobj2)

        self.assertEqual(self.repo.numGameObj, 2)

    def test_useWeakrefGettingFromRepository(self):       
        print self.gobjwref()
        self.assertIsNotNone(self.gobjwref())

        #weakref의 사용
        another = self.gobjwref
        print another

        ### DON'T TRY THIS ###
        print '!', sys.getrefcount(self.gobjwref())
        self.strong = self.gobjwref() #이렇게 변수에 할당하지 마시오.
        print '!', sys.getrefcount(self.gobjwref())
        del self.strong
        print "don't try this", self.gobjwref()

    def test_removeGameObjUsingWeakref(self):
        #repository 원소 수 변수 조절
        beforeNum = self.repo.numGameObj
        self.repo.remove(self.gobjwref)
        afterNum = self.repo.numGameObj
        self.assertEqual(afterNum, beforeNum - 1)
        
        #repo.remove함수는 weakref 타입만 받아들인다.
        self.assertRaises(AssertionError, self.repo.remove, 1)

        #이미 제거된 원소는 다시 제거할 수 없다
        self.assertRaises(KeyError, self.repo.remove, self.gobjwref)

    def test_clearRepository(self):
        # 10개 추가
        count = 10
        before = self.repo.numGameObj

        wrefList = []
        for i in range(count):
            wrefList.append( self.repo.add(GameObject()) )

        after = self.repo.numGameObj
        self.assertEqual(after, before + count)
        
        #모두 삭제
        self.repo.clear()
        self.assertEqual(self.repo.numGameObj, 0)

        #정말로 제거되었는가?
        for wref in wrefList:
            self.assertRaises(KeyError, self.repo.remove, wref)
                    
    def test_addDuplicatedElements(self):
        #중복되는 게임오브젝트를 add할 경우 
        gobj2 = gobj3 = GameObject()
        wref = self.repo.add(gobj2)        
        wref2 = self.repo.add(gobj3)
        #동일한 약한참조가 반환된다.
        self.assertEqual(wref,wref2)
                

if __name__ == '__main__':
    unittest.main()
