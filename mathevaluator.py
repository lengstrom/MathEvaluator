import sublime, sublime_plugin
from pyparsing import Literal,CaselessLiteral,Word,Combine,Group,Optional,\
	ZeroOrMore,Forward,nums,alphas
import math
import operator

exprStack = []

def pushFirst( strg, loc, toks ):
	exprStack.append( toks[0] )
def pushUMinus( strg, loc, toks ):
	if toks and toks[0]=='-': 
		exprStack.append( 'unary -' )
		#~ exprStack.append( '-1' )
		#~ exprStack.append( '*' )

bnf = None
def BNF():
	"""
	expop   :: '^'
	multop  :: '*' | '/'
	addop   :: '+' | '-'
	integer :: ['+' | '-'] '0'..'9'+
	atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
	factor  :: atom [ expop factor ]*
	term    :: factor [ multop factor ]*
	expr    :: term [ addop term ]*
	"""
	global bnf
	if not bnf:
		point = Literal( "." )
		e     = CaselessLiteral( "E" )
		fnumber = Combine( Word( "+-"+nums, nums ) + 
						   Optional( point + Optional( Word( nums ) ) ) +
						   Optional( e + Word( "+-"+nums, nums ) ) )
		ident = Word(alphas, alphas+nums+"_$")
	 
		plus  = Literal( "+" )
		minus = Literal( "-" )
		mult  = Literal( "*" )
		div   = Literal( "/" )
		lpar  = Literal( "(" ).suppress()
		rpar  = Literal( ")" ).suppress()
		addop  = plus | minus
		multop = mult | div
		expop = Literal( "^" )
		pi    = CaselessLiteral( "PI" )
		
		expr = Forward()
		atom = (Optional("-") + ( pi | e | fnumber | ident + lpar + expr + rpar ).setParseAction( pushFirst ) | ( lpar + expr.suppress() + rpar )).setParseAction(pushUMinus) 
		
		# by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
		# that is, 2^3^2 = 2^(3^2), not (2^3)^2.
		factor = Forward()
		factor << atom + ZeroOrMore( ( expop + factor ).setParseAction( pushFirst ) )
		
		term = factor + ZeroOrMore( ( multop + factor ).setParseAction( pushFirst ) )
		expr << term + ZeroOrMore( ( addop + term ).setParseAction( pushFirst ) )
		bnf = expr
	return bnf

# map operator symbols to corresponding arithmetic operations
epsilon = 1e-12
opn = { "+" : operator.add,
		"-" : operator.sub,
		"*" : operator.mul,
		"/" : operator.truediv,
		"^" : operator.pow }
fn  = { "sin" : math.sin,
		"cos" : math.cos,
		"tan" : math.tan,
		"abs" : abs,
		"trunc" : lambda a: int(a),
		"round" : round,
		"sgn" : lambda a: abs(a)>epsilon and cmp(a,0) or 0}
def evaluateStack( s ):
	op = s.pop()
	if op == 'unary -':
		return -evaluateStack( s )
	if op in "+-*/^":
		op2 = evaluateStack( s )
		op1 = evaluateStack( s )
		return opn[op]( op1, op2 )
	elif op == "PI":
		return math.pi # 3.1415926535
	elif op == "E":
		return math.e  # 2.718281828
	elif op in fn:
		return fn[op]( evaluateStack( s ) )
	elif op[0].isalpha():
		return 0
	else:
		return float( op )

def test( s):
	try:
		global exprStack
		exprStack = []
		results = BNF().parseString( s )
		val = evaluateStack( exprStack[:] )
		return val
	except:
		return False
  
class mathevaluatorCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			if not region.empty():
				s = self.view.substr(region)
				strlen = len(s)
				i = 0

				#Parser has some issues with decimals
				while i != strlen:
					if s[i] == '.':
						if i == 0:
							print "@1"
							s = "0" + s
							strlen = strlen + 1
							i = i + 1
						else:
							print "@2"
							if not s[i - 1].isdigit():
								strlen = strlen + 1
								i = i + 1
								s = s[:i - 1] + '0' + s[i - 1:]
					i = i + 1
					
				evaluated = str(test(s))
				if evaluated != 'None' and evaluated != 'False':
					if str(evaluated)[-2:] == ".0":
						evaluated = str(evaluated)[:-2]
					dotpos = evaluated.find('.')
					if dotpos != -1:
						evaluated = evaluated[:dotpos + 5]
					self.view.replace(edit, region, evaluated)