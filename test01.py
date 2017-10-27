__author__ = 'xiejun'

with open("data.txt", 'r') as f:
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
    d = {}
    s = ('xxx', 'yyy', 'zzz')
    print('xxx' in s)