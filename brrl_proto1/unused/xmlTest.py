import unittest
import xml.etree.ElementTree as eltree

class Test_xmlTest(unittest.TestCase):
    def test_eltree(self):
        tree = eltree.parse('unit_test\eltreeTest.xml')
        root = tree.getroot()

        print 'wtf?'
        print root.tag
        print type(root[0][0].text)
        print root[0][0].text
        print root[0][1].text

        print root[0][2].tag
        print root[0][2][0].text

if __name__ == '__main__':
    unittest.main()
