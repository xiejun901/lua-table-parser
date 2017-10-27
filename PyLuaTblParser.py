__author__ = 'xiejun'

class PythonError(Exception):
    def __str__(self):
        return repr('python to lua error')

class LuaError(Exception):
    def __str__(self):
        return repr('lua to python error')

class STATE(object):
    START        = 0

    SINGLE_ZERO  = 1
    PRE_HEX      = 2
    HEX_NUM      = 3
    SIGN         = 4
    NUMBER       = 5
    PRE_FLOAT    = 6
    FLOAT        = 7
    E_FLOAT_PRE  = 8
    E_FLOAT_SIGN = 9
    E_FLOAT      = 10

    # STR_SINGLE_QUAT_PRE = 11
    # STR_SINGLE_QUAT     = 12
    # STR_DOUBLE_QUAT_PRE = 13
    # STR_DOUBLE_QUAT     = 14
    # STR_BRACKET_PRE     = 15
    # STR_BRACKET         = 16

class PyLuaTblParser(object):

    def __init__(self):
        self.pythonDict = {}
        self.luaTbl = ""

    def loadDict(self, d):
        self.pythonDict = d

    def dump(self):
        self.luaTbl = ""
        self.dump_aux(self.pythonDict)
        return self.luaTbl

    def dump_aux(self, obj):
        if isinstance(obj, list):
            self.luaTbl += '{'
            for element in obj:
                self.dump_aux(element)
                self.luaTbl += ', '
            self.luaTbl += '}'
        elif isinstance(obj, dict):
            self.luaTbl += '{'
            for k, v in obj.items():
                if self.dumpKey(k):
                    self.luaTbl += ' = '
                    self.dump_aux(v)
                    self.luaTbl += ','
            self.luaTbl += '}'
        else:
            self.dumpValue(obj)


    def dumpKey(self, k):
        if isinstance(k, int) or isinstance(k, float):
            self.luaTbl = self.luaTbl + '[' + str(k) + ']'
            return True
        elif isinstance(k, str):
            self.luaTbl += k
            return True
        return False

    def dumpValue(self, v):
        if v is None:
            self.luaTbl += 'nil'
        elif isinstance(v, bool):
            self.luaTbl += (str(v).lower())
        elif isinstance(v, int) or isinstance(v, float):
            self.luaTbl += str(v)
        elif isinstance(v, str):
            self.luaTbl += '"'+v+'"'
        else:
            raise PythonError()

    def equals(self, s, begin, end, t):
        #check boundary and judge is tow string equals
        if end > len(s):
            return False
        return s[begin:end] == t

    def getString(self, s, begin):
        begin  = self.escapeBlankAndComment(s, begin)
        escapeList = {
			'\\"': '\"',
			"\\'": "\'",
			"\\b": "\b",
			"\\f": "\f",
			"\\r": "\r",
			"\\n": "\n",
			"\\t": "\t",
			"\\u": "u",
			"\\\\":"\\",
			"\\/": "/",
			"\\a": "\a",
			"\\v": "\v"
		}
        l = []
        if self.equals(s,begin,begin+2,'[['):
            begin += 2
            while begin < len(s):
                if self.equals(s,begin, begin+2, ']]'):
                    return ''.join(l), begin+2
                elif s[begin] == '\\':
                    if s[begin:begin+2] in escapeList:
                        l.append(escapeList[s[begin:begin+2]])
                        begin += 2
                    else:
                        raise LuaError()
                else:
                    l.append(s[begin])
                    begin += 1
            raise LuaError()
        elif self.equals(s, begin,begin+1,'"'):
            begin += 1
            while begin < len(s):
                if s[begin] == '"':
                    return ''.join(l), begin+1
                elif s[begin] == '\\':
                    if s[begin:begin+2] in escapeList:
                        l.append(escapeList[s[begin:begin+2]])
                        begin += 2
                    else:
                        raise LuaError()
                else:
                    l.append(s[begin])
                    begin += 1
            raise LuaError()
        elif self.equals(s, begin, begin+1, "'"):
            begin += 1
            while begin < len(s):
                if s[begin] == "'":
                    return ''.join(l), begin + 1
                elif s[begin] == '\\':
                    if s[begin:begin+2] in escapeList:
                        l.append(escapeList[s[begin:begin+2]])
                        begin += 2
                    else:
                        raise LuaError()
                else:
                    l.append(s[begin])
                    begin += 1
            raise LuaError()
        else:
            return None, begin

    def getStringShortHand(self, s, begin):
        # deal {x = "123"}
        end = begin
        if s[end] == '_' or s[end].isalpha():
            end += 1
            while s[end] == '_' or s[end].isdigit() or s[end].isalpha():
                end += 1
            return s[begin:end], end
        else:
            return None, end




    def getNumber(self, s, begin):
        state = STATE.START
        end = begin
        while end < len(s):
            if state == STATE.START:
                if s[end] == ' ':
                    state = STATE.START
                elif s[end] == '0':
                    state = STATE.SINGLE_ZERO
                elif s[end] in '123456789':
                    state = STATE.NUMBER
                elif s[end] == '.':
                    state = STATE.PRE_FLOAT
                elif s[end] == '-':
                    state = STATE.SIGN
                else:
                    return None, begin
            elif state == STATE.SINGLE_ZERO:
                if s[end] in 'Xx':
                    state = STATE.PRE_HEX
                elif s[end] in '0123456789':
                    state = STATE.NUMBER
                elif s[end] == '.':
                    state = STATE.PRE_FLOAT
                elif s[end] in 'Ee':
                    state = STATE.E_FLOAT_PRE
                elif s[end] in ' /t,{}':
                    return int(s[begin:end]), end
                else:
                    raise LuaError()
            elif state == STATE.PRE_HEX:
                if s[end] in '0123456789abcdABCD':
                    state = STATE.HEX_NUM
                else:
                    raise LuaError()
            elif state == STATE.HEX_NUM:
                if s[end] in '0123456789abcdefABCDEF':
                    state = STATE.HEX_NUM
                elif s[end] in ' /t,{}':
                    return int(s[begin:end]), end
                else:
                    raise LuaError()
            elif state == STATE.SIGN:
                if s[end] in '0123456789':
                    state = STATE.NUMBER
                else:
                    raise LuaError
            elif state == STATE.NUMBER:
                if s[end] in '0123456789':
                    pass
                elif s[end] == '.':
                    state = STATE.PRE_FLOAT
                elif s[end] in 'Ee':
                    state = STATE.E_FLOAT_PRE
                elif s[end] in ' /t,{}[]':
                    return int(s[begin:end]), end
                else:
                    raise LuaError()
            elif state == STATE.PRE_FLOAT:
                if s[end] in '0123456789':
                    state = STATE.FLOAT
                else:
                    raise LuaError()
            elif state == STATE.FLOAT:
                if s[end] in '0123456789':
                    pass
                elif s[end] in 'Ee':
                    state = STATE.E_FLOAT_PRE
                elif s[end] in ' /t,{}':
                    return float(s[begin:end]), end
                else:
                    raise LuaError()
            elif state == STATE.E_FLOAT_PRE:
                if s[end] =='-':
                    state = STATE.E_FLOAT_SIGN
                elif s[end] in '0123456789':
                    state = STATE.E_FLOAT
                else:
                    raise LuaError()
            elif state == STATE.E_FLOAT_SIGN:
                if s[end] in '0123456789':
                    state = STATE.E_FLOAT
                else:
                    raise LuaError()
            elif state == STATE.E_FLOAT:
                if s[end] in '0123456789':
                    pass
                elif s[end] in ' /t,{}':
                    return float(s[begin:end]), end
            else:
                raise LuaError()
            end+=1

    def isDigit(self, ch):
        return ch >= '0' and ch <= '9'

    def escapeBlank(self, s, begin):
        while begin < len(s) and s[begin].isspace():
            begin += 1
        return begin

    def escapeComment(self, s, begin):
        return begin

    def escapeBlankAndComment(self, s, begin):
        while begin < len(s):
            begin = self.escapeBlank(s, begin)
            if self.equals(s, begin, begin+2, '--'):
                begin = self.escapeComment(s, begin)
            else:
                break
        return begin

    def isEqual(self, s, begin, t):
        end = begin + len(t)
        if end > len(s):
            return False
        return s[begin:end] == t

    def getNil(self, s, begin):
        '''
        get lua nil
        '''
        begin = self.escapeBlankAndComment(s, begin)
        if s[begin:begin + 3] == 'nil':
            return 'nil', begin + 3
        else:
            return None, begin

    def getBool(self, s, begin):
        '''
        get bool
        '''
        result, end = self.getStringShortHand(s, begin)
        if result == 'true':
            return True, end
        if result == 'false':
            return False, end
        return None, begin




    def getValue(self, s, begin):
        begin = self.escapeBlankAndComment(s, begin)
        if s[begin] == '{':
            return self.getTable(s, begin)
        value, begin = self.getNumber(s, begin)
        if value == None:
            value, begin = self.getString(s, begin)
        return value, begin

    def getTable(self, s, begin):
        begin = self.escapeBlankAndComment(s, begin)
        d = {}
        isList = True
        index = 1
        if s[begin] != '{':
            raise LuaError()
        begin += 1
        while begin < len(s):
            begin = self.escapeBlankAndComment(s, begin)
            if s[begin] == '}':
                if d and isList:
                    li = []
                    for i in d.keys():
                        li.append(i)
                    return li, begin + 1
                else:
                    di = {}
                    for k, v in d.iteritems():
                        di[k] = v
                    return di, begin + 1
            elif s[begin] in ',;':
                begin += 1
            elif s[begin] == '{':
                value, begin = self.getTable(s, begin)
                d[index] = value
                index += 1
            elif self.equals(s, begin, begin+2, '[[') or s[begin] == '"' or s[begin] == "'":
                value, begin = self.getString(s, begin)
                d[index] = value
                index += 1
            elif s[begin] == '[':
                isList = False
                begin += 1
                begin = self.escapeBlankAndComment(s, begin)
                key, begin = self.getNumber(s, begin)
                if key == None:
                    key, begin = self.getString(s, begin)
                begin = self.escapeBlankAndComment(s, begin)
                if s[begin] != ']':
                    raise LuaError()
                begin += 1
                begin = self.escapeBlankAndComment(s, begin)
                if s[begin] != '=':
                    raise LuaError()
                begin += 1
                value, begin = self.getValue(s, begin)
                d[key] = value
            elif s[begin] == '_' or s[begin].isalpha():
                isList = False
                key, begin = self.getStringShortHand(s, begin)
                begin = self.escapeBlankAndComment(s, begin)
                if s[begin] != '=':
                    raise LuaError()
                begin += 1
                begin = self.escapeBlankAndComment(s, begin)
                value, begin = self.getValue(s, begin)
                d[key] = value
            else:
                value, begin = self.getValue(s, begin)
                if value == None:
                    raise LuaError()
                d[index] = value
                index += 1
























if __name__ == '__main__':
    d = {
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
    print(d)
    paser = PyLuaTblParser()
    paser.loadDict(d)
    print(paser.dump())