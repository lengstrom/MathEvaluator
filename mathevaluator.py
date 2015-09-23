import sublime, sublime_plugin
import math
import operator
import sys
import pdb

# # infix operators =
# +
# -
# /
# *
# %
# ^
# >>

# # operators

# Math(*)
# ln()
# 0b
# 0x

# #datatypes
# numbers
# normal
# variables
# pi = Math.PI

class Atom:
    def __init__(self, value, type_):
        self.type_ = type_
        if self.type_ == "value":
            if type(value) == str:
                if len(value) >= 2:
                    if value[0] == "0":
                        if value[1] == "b":
                            self.value = eval('0b' + str(int(value[2:])))
                        elif value[1] == "x":
                            self.value = eval('0x' + str(int(value[2:])))
                        elif value[1] in "0123456789":
                            self.value = eval('0' + str(int(value[1:])))
                    else:
                        self.value = float(value)
                else:
                    self.value = float(value)
            else:
                self.value = value
        else:
            self.value = value


environment = {
    "+":Atom(operator.add,"infix"),
    "-":Atom(operator.sub,"infix"),
    "/":Atom(operator.truediv,"infix"),
    "*":Atom(operator.mul,"infix"),
    "&":Atom(lambda x, y: operator.and_(int(x), int(y)),"infix"),
    "^":Atom(lambda x, y: operator.xor(int(x), int(y)),"infix"),
    "|":Atom(lambda x, y: operator.or_(int(x), int(y)),"infix"),
    "~":Atom(lambda x: operator.invert(int(x)),"prefix"),
    # "-":Atom(operator.neg,"prefix"),
    # "+":Atom(operator.neg,"prefix"),
    #"0b":Atom(lambda x: eval("0b"+str(int(x))),"prefix"),
    #"0x":Atom(lambda x: eval("0x"+str(int(x))),"prefix"),
    "ln":Atom(math.log, "prefix"),
    "sqrt":Atom(math.sqrt, "prefix"),
    "pi":Atom(math.pi, "value"),
    "**":Atom(operator.pow,"infix"),
}

precedence = {environment['ln']:2, environment['sqrt']:2, environment['~']:2, environment["**"]:1, environment["*"]:0, environment["/"]:0}
separators = ["(", ")"]
keywords = environment.keys()

def atomize(s):
    try:
        return environment[s]
    except:
        return Atom(s, "value")
    
# separators
def tokenize(s):
    s = "(" + s + ")"
    token = ''
    for i in (separators + keywords):
        s = s.replace(i, " " + i + " ")

    s = s.split()
    last = None
    nums = []
    for i in range(len(s)):
        if s[i] == last and not last in separators:
            nums.append(i-1)
        last = s[i]
        
    offset = 0
    for i in nums:
        i = i + offset
        s = s[:i]  + [s[i] * 2] + s[i+2:]
        offset = offset - 1

    return s

def read_from_tokens(tokens):
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ")":
            L.append(read_from_tokens(tokens))
        tokens.pop(0)
        return L
    elif token == ')':
        raise ValueError()
    else:
        return atomize(token)

def eval_(a, b, li):
    if type(b) == list:
        c = b.pop(0)
        val = eval_(None, c, b)
        if len(li) != 0:
            c_ = li.pop(0)
            return eval_(val, c, li)
        else:
            return val
    else:
        if b.type_ == "value":
            val = b.value
            if len(li) == 0:
                return val
            else: 
                c = li.pop(0)
                return eval_(val, c, li)
        else:
            if len(li) >= 2:
                op = li[0]
                if type(op) != list and op in precedence and (not b in precedence or precedence[op] > precedence[b]):
                    a_ = li.pop(0)
                    b_ = li.pop(0)
                    li.insert(0, atomize(eval_(b, a_, [b_])))
            if len(li) >= 3:
                op = li[1]
                if type(op) != list and op in precedence and (not b in precedence or precedence[op] > precedence[b]):
                    a_ = li.pop(0)
                    b_ = li.pop(0)
                    c_ = li.pop(0)
                    li.insert(0,atomize(eval_(eval_(b, a_, []), b_, [c_])))
            if b.type_ == "infix":
                c = li.pop(0)
                val = b.value(a, eval_(b, c, []))
                if len(li) != 0:
                    c_ = li.pop(0)
                    return eval_(val, c_, li)
                else:
                    return val
            elif b.type_ == "prefix":
                c = li.pop(0)
                val = b.value(eval_(b, c, []))
                if len(li) != 0:
                    c_ = li.pop(0)
                    return eval_(val, c_, li)
                else:
                    return val

def eval_string(s):
    tokens = tokenize(s)
    ast = read_from_tokens(tokens)
    value = eval_(None, ast, [])
    return value
    
class mathevaluatorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)
                strlen = len(s)
                i = 0
                while i != strlen:
                    if s[i] == '.':
                        if i == 0:
                            s = "0" + s
                            strlen = strlen + 1
                            i = i + 1
                        else:
                            if not s[i - 1].isdigit():
                                strlen = strlen + 1
                                i = i + 1
                                s = s[:i - 1] + '0' + s[i - 1:]
                    i = i + 1
                try:
                    evaluated = str(eval_string(s))
                    if str(evaluated)[-2:] == ".0":
                        evaluated = str(evaluated)[:-2]
                    self.view.replace(edit, region, evaluated)
                except:
                    pass

def test(a, b):
    t = eval_string(a) == b
    if t:
        print "Test %s passed!" % a

if __name__ == "__main__" and "test" in sys.argv:
    test("ln(3)", math.log(3))
    test("ln(3) / ln(3)", 1)
    test("2 * (33 + 33)**2", 2 * (33 + 33)**2)
    test("0b01101*0x33", 0b01101*0x33)
    test("0b01101*~0x33", 0b01101*~0x33)
