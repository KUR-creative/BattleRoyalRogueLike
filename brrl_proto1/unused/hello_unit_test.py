#-*- coding: utf-8 -*-
import unittest
from mockito import * 
#네임스페이스 mock 명시 없이 쓸 수 있게 된다.

def sum(a,b):
    return a+b

class Test_hello_unit_test(unittest.TestCase):
    def test_A(self):
        print "a"
        self.assertEqual(3,3)

    def test_sum(self):
        self.assertEqual(sum(1,2),3, "\n\n##!")

    def test_mockito(self):
        math = Mock()
        when(math).add(1,2).thenReturn(3)
        #self.assertEqual(math.add(1,2), 0, 'mockito test')
        verify(math).add(1,2)

if __name__ == '__main__':
    unittest.main()
