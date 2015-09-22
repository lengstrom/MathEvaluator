#import sublime, sublime_plugin
import math
import operator


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
        self.value = value

environment = {
    "+":Atom(operator.add,"infix"),
    "-":Atom(operator.sub,"infix"),
    "/":Atom(operator.truediv,"infix"),
    "*":Atom(operator.mul,"infix"),
    "&":Atom(lambda x, y: operator.and_(int(x), int(y)),"infix"),
    "^":Atom(lambda x, y: operator.xor(int(x), int(y)),"infix"),
    "|":Atom(lambda x, y: operator.or_(int(x), int(y)),"infix"),
    "~":Atom(lambda x: operator.invert(int(x)),"leftfix"),
    # "-":Atom(operator.neg,"leftfix"),
    # "+":Atom(operator.neg,"leftfix"),
    "0b":Atom(lambda x: eval("0b"+str(int(x))),"leftfix"),
    "0x":Atom(lambda x: eval("0x"+str(int(x))),"leftfix"),
    "ln":Atom(math.log, "leftfix"),
    "sqrt":Atom(math.sqrt, "leftfix"),
    "pi":Atom(math.pi, "value"),
    "**":Atom(operator.pow,"infix"),
}

precedence = {environment["**"]:0}
separators = ["(", ")"]
keywords = environment.keys()

def atomize(s):
    try:
        return environment[s]
    except:
        return Atom(float(s), "value")
    
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
            if len(li) >= 3:
                op = li[1]
                if op in precedence and (not b in precedence or precedence[op] > precedence[b]):
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
            elif b.type_ == "leftfix":
                c = li.pop(0)
                val = b.value(eval_(b, c, []))
                if len(li) != 0:
                    c_ = li.pop(0)
                    return eval_(val, c_, li)
                else:
                    return val
        
    
# class mathevaluatorCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         for region in self.view.sel():
#             if not region.empty():
#                 s = self.view.substr(region)
#                 strlen = len(s)
#                 i = 0
#                 while i != strlen:
#                     if s[i] == '.':
#                         if i == 0:
#                             s = "0" + s
#                             strlen = strlen + 1
#                             i = i + 1
#                         else:
#                             if not s[i - 1].isdigit():
#                                 strlen = strlen + 1
#                                 i = i + 1
#                                 s = s[:i - 1] + '0' + s[i - 1:]
#                     i = i + 1

#                 evaluated = str(evaluate_string(s))
#                 if evaluated != 'None' and evaluated != 'False':
                    
#                     if str(evaluated)[-2:] == ".0":
#                         evaluated = str(evaluated)[:-2]
#                     self.view.replace(edit, region, evaluated)

if __name__ == "__main__":
    a = read_from_tokens(tokenize("3 * (4 + 3)**(2+2)"))
    print eval_(None, a, [])
