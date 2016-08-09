#-*- coding: utf-8 -*-
# 이거를 start file로 실행하면 
# unit_test_path에 있는 모든 테스트들이 실행된다.
import unittest

unit_test_path = 'unit_test'

if __name__ == "__main__":
    all_tests = unittest.TestLoader().discover(unit_test_path, pattern='*.py')
    unittest.TextTestRunner().run(all_tests)