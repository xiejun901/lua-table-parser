__author__ = 'xiejun'

import unittest
from PyLuaTblParser import PyLuaTblParser


class TestPaser(unittest.TestCase):

    def test_dump(self):
        case = {}
        ans  = {}
        case[0] = {
            "array": [65, 23, 5],
            "dict": {
                "mixed": {
                    1: 43,
                    2: 54.33,
                    3: False,
                    4: 9,
                    "string": "value"
                },
                "array": [3, 6, 4],
                "string": "value"
            }
        }
        ans[0] = '''
            {
                array = {
                    65, 23, 5,
                    },
                dict = {
                    mixed = {
                        [1] = 43,
                        [2] = 54.33,
                        [3] = false,
                        [4] = 9,
                        "string" = "value",
                    },
                array = {3, 6, 4, },
                string = "value",
                },
            }
        '''
        case[1] = {
            "list": [1,2,3,4,None,"string"],
            32:[None,3,4],
            31.5:{0:"a", 1:"b"}
        }
        ans[1] = '''
            {
                "list"={1,2,3,4,nil,"string"},
                [32] = {nil,3,4},
                [31.5] = {
                    [0]="a",
                    [1]="b",
                    },
            }
        '''
        parserObj = PyLuaTblParser()
        for i in range(2):
            parserObj.loadDict(case[i])
            s = parserObj.dump()
            self.assertTrue("".join(s.split()),"".join(ans[i].split()))

    def test_getNumber(self):
        parserObj = PyLuaTblParser()
        s = '123 '
        result, end = parserObj.getNumber(s,0)
        self.assertTrue(result == 123 and end == 3)
        s = '123.45 '
        result, end = parserObj.getNumber(s,1)
        self.assertTrue(result == 23.45 and end == 6)
        s = '123.45 '
        result, end = parserObj.getNumber(s,1)
        self.assertTrue(result == 23.45 and end == 6)
        s = '-123.45e2 '
        result, end = parserObj.getNumber(s,0)
        self.assertTrue(result == -12345 and end == 9)
        s = '.05 '
        result, end = parserObj.getNumber(s,0)
        self.assertTrue(result == 0.05 and end == 3)
        s = r'"  abcd"'
        result = parserObj.getNumber(s, 0)
        print result

    def test_getString(self):
        parseObj = PyLuaTblParser()
        s = '\'abcde"xyz\''
        result, end = parseObj.getString(s,0)
        self.assertTrue(result == 'abcde"xyz')
        self.assertTrue(end == 11)
        s = r'    "e\n\'\'"'
        result = parseObj.getString(s,0)
        print result

    def test_getTable(self):
        parseObj = PyLuaTblParser()
        s = r'{[3]=1,[4]=2,[5]=3,}'
        result = parseObj.getTable(s, 0)
        print result
        s = r'{[3] = "xyz", ["xx"] = "sdb", yy = "fund", 123} '
        result = parseObj.getTable(s, 0)
        print result


if __name__ == '__main__':
    unittest.main()
