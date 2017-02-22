# Submission for Jill Mao - Student ID: 930891998 and 
# Rebecca Youngerman - Student ID: 930921312

# Your task is to construct the remaining recursive descent routines 
# to complete the parser for the Gee implementation grammar. You are 
# free to modify the grammar provided you do nochange the syntax of Gee.


import re, sys, string

debug = False
dict = { }
tokens = [ ]


class StatementList( object ):
	def __init__(self):
		self.statementList = []

	def addStatement(self, statement):
		self.statementList.append(statement)

	def __str__(self):
		printStr = ''
		for statement in self.statementList:
			printStr += str(statement)
		return printStr
	
# Statement class and subclasses

class Statement( object ):
	def __str__(self):
		return ""

class Assignment( Statement ):
	def __init__(self, identifier, expression):
		self.identifier = identifier
		self.expression = expression
		
	def __str__(self):
		return "= " + str(self.identifier) + " " + str(self.expression) + "\n"

class WhileStatement( Statement ):
	def __init__(self, expression, block):
		self.expression = expression
		self.block = block

	def __str__(self):
		return "while " + str(self.expression) + "\n" + str(self.block) + "endwhile\n"


class IfStatement( Statement ):
	def __init__(self, expression, ifBlock, elseBlock):
		self.expression = expression
		self.ifBlock = ifBlock
		self.elseBlock = elseBlock

	def __str__(self):
		if self.elseBlock == None:
			return "if " + str(self.expression) + "\n" + str(self.ifBlock) + "endif\n"
		else:
			return "if " + str(self.expression) + "\n" + str(self.ifBlock) + "else\n" + str(self.elseBlock) + "endif\n"

	
# Expression class and its subclasses
class Expression( object ):
	def __str__(self):
		return "" 
	
class BinaryExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)

class Number( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)

class VarRef( Expression ) :
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return str(self.value)
	
class String( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)
	




# Parse routines for the expression nonterminals
	
def factor( ):
	"""factor     = number | string | ident |  "(" expression ")" """

	tok = tokens.peek( )
	
	if debug: print ("Factor: ", tok)
	
	if re.match(Lexer.number, tok):
		expr = Number(tok)
		tokens.next( )
		return expr
	
	if re.match(Lexer.string, tok):
		expr = String(tok)
		tokens.next( )
		return expr
	
	if re.match(Lexer.identifier, tok):
		expr = VarRef(tok)
		tokens.next( )
		return expr
	
	if tok == "(":
		tokens.next( )  # or match( tok )
		expr = expression( )
		tokens.peek( )
		tok = match(")")
		return expr
	error("Invalid operand")
	return


def term( ):
	""" term    = factor { ('*' | '/') factor } """

	tok = tokens.peek( )
	
	if debug: print ("Term: ", tok)
	left = factor( )
	tok = tokens.peek( )
	
	while tok == "*" or tok == "/":
		tokens.next()
		right = factor( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def andExpr( ):
	""" relationalExpr { "and" relationalExpr } """
	tok = tokens.peek( )
	
	if debug: print ("andExpr: ", tok)
	left = relationalExpr( )
	tok = tokens.peek( )	
	
	while tok == "and":
		tokens.next()
		right = relationalExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left	

def expression( ):
	""" andExpr { "or" andExpr } """
	tok = tokens.peek( )
	
	if debug: print ("expression: ", tok)
	left = andExpr( )
	tok = tokens.peek( )	
	
	while tok == "or":
		tokens.next()
		right = andExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left
	


def addExpr( ):
	""" addExpr    = term { ('+' | '-') term } """
	tok = tokens.peek( )
	
	if debug: print ("addExpr: ", tok)
	left = term( )
	tok = tokens.peek( )
	
	while tok == "+" or tok == "-":
		tokens.next()
		right = term( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def relationalExpr( ):
	""" relationalExpr = addExpr [ relation addExpr ]"""
	tok = tokens.peek( )
	
	if debug: print ("relationalExpr: ", tok)
	left = addExpr( )
	tok = tokens.peek( )
	
	while re.match(Lexer.relational, tok):
		tokens.next()
		right = addExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek()
	return left

		

# Parse routines for statements

def parseStmtList( ):
	""" stmtList = { statement } """
	tok = tokens.peek( )
	statementList = StatementList()
	
	while tok != None and tok != "~":
		statement = parseStatement()
		statementList.addStatement(statement)
		tok = tokens.peek()
	return statementList

def parseStatement():
	""" statement 	= assign | ifStatement |  whileStatement """
	tok = tokens.peek ( )
	
	if debug: print ("Statement: ", tok)
	
	if tok == "if":
		return parseIfStatement()
	
	if tok == "while":
		return parseWhileStatement()
	
	elif re.match(Lexer.identifier, tok):
		return parseAssign()
	
def parseAssign():
	"""assign = ident "=" expression  eoln"""
	ident = tokens.peek()
	
	if debug: print ("Assign statement: ", ident)
	
	if tokens.next() != "=":
		error("Assignment has no equal sign")
	tokens.next()
	expr = expression()
	tok = tokens.peek()
	
	if tok != ";":
		error("Assignment does not end with EOL.")
	tokens.next()
	return Assignment(ident,expr)
	
	
	
	
def parseIfStatement():
	""""if" expression block   [ "else" block ]"""
	tok = tokens.next()
	
	if debug: print ("If Statement: ", tok)
	expr = expression()
	ifBlock = parseBlock()
	elseBlock = None
	
	if tokens.peek() == "else":
		tok = tokens.next()
		
		if debug: print ("Else statement: ", tok)
		elseBlock = parseBlock()
		
	return IfStatement(expr, ifBlock, elseBlock)

def parseWhileStatement():
	"""whileStatement = "while"  expression  block"""
	tok = tokens.next()
	
	if debug: print ("While statement: ", tok)
	expect = expression()
	block = parseBlock()
	return WhileStatement(expect, block)


def parseBlock():
	"""block = ":" eoln indent stmtList undent"""
	tok = tokens.peek()
	
	if debug: print ("Block: ", tok)
	
	if tok != ":":
		error("Block is missing ':'.")
	tok = tokens.next()
	
	if tok != ";":
		error("Block is missing EOL character.")
	tok = tokens.next()
	
	if tok != "@":
		error("Block is not indented after EOL.")
	tok = tokens.next()
	stmtList = parseStmtList()
	
	if tokens.peek() != "~":
		error("Block is not undented after statements.")
	tokens.next()
	return stmtList
	
# The "parse" function. This builds a list of tokens from the input string,
# and then hands it to a recursive descent parser for the PAL grammar.	
	

def parse( text ) :
	global tokens
	tokens = Lexer( text )
	#expr = expression( )
	#print (str(expr))
	#     Or:
	stmtlist = parseStmtList( )
	print (stmtlist)
	return

# Other supporting methods

def error( msg ):
	#print msg
	sys.exit(msg)



def match(matchtok):
	tok = tokens.peek( )
	
	if (tok != matchtok): error("Expecting "+ matchtok)
	tokens.next( )
	return tok


# Lexer, a private class that represents lists of tokens from a Gee
# statement. This class provides the following to its clients:
#
#   o A constructor that takes a string representing a statement
#       as its only parameter, and that initializes a sequence with
#       the tokens from that string.
#
#   o peek, a parameterless message that returns the next token
#       from a token sequence. This returns the token as a string.
#       If there are no more tokens in the sequence, this message
#       returns None.
#
#   o removeToken, a parameterless message that removes the next
#       token from a token sequence.
#
#   o __str__, a parameterless message that returns a string representation
#       of a token sequence, so that token sequences can print nicely

class Lexer :
	

	# The constructor with some regular expressions that define Gee's lexical rules.
	# The constructor uses these expressions to split the input expression into
	# a list of substrings that match Gee tokens, and saves that list to be
	# doled out in response to future "peek" messages. The position in the
	# list at which to dole next is also saved for "nextToken" to use.
	
	special = r"\(|\)|\[|\]|,|:|;|@|~|;|\$"
	relational = "<=?|>=?|==?|!="
	arithmetic = "\+|\-|\*|/"
	#char = r"'."
	string = r"'[^']*'" + "|" + r'"[^"]*"'
	number = r"\-?\d+(?:\.\d+)?"
	literal = string + "|" + number
	#idStart = r"a-zA-Z"
	#idChar = idStart + r"0-9"
	#identifier = "[" + idStart + "][" + idChar + "]*"
	identifier = "[a-zA-Z]\w*"
	lexRules = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier
	
	def __init__( self, text ) :
		self.tokens = re.findall( Lexer.lexRules, text )
		self.position = 0
		self.indent = [ 0 ]
	
	
	# The peek method. This just returns the token at the current position in the
	# list, or None if the current position is past the end of the list.
	
	def peek( self ) :
		if self.position < len(self.tokens) :
			return self.tokens[ self.position ]
		else :
			return None
				
	
	
	# The removeToken method. All this has to do is increment the token sequence's
	# position counter.
	
	def next( self ) :
		self.position = self.position + 1
		return self.peek( )
	
	
	# An "__str__" method, so that token sequences print in a useful form.
	
	def __str__( self ) :
		return "<Lexer at " + str(self.position) + " in " + str(self.tokens) + ">"



def chkIndent(line):
	ct = 0
	for ch in line:
		if ch != " ": return ct
		ct += 1
	return ct
		

def delComment(line):
	pos = line.find("#")
	if pos > -1:
		line = line[0:pos]
		line = line.rstrip()
	return line

def mklines(filename):
	inn = open(filename, "r")
	lines = [ ]
	pos = [0]
	ct = 0
	for line in inn:
		ct += 1
		line = line.rstrip( )+";"
		line = delComment(line)
		
		if len(line) == 0 or line == ";": continue
		indent = chkIndent(line)
		line = line.lstrip( )
		
		if indent > pos[-1]:
			pos.append(indent)
			line = '@' + line
			
		elif indent < pos[-1]:
			
			while indent < pos[-1]:
				del(pos[-1])
				line = '~' + line
		# edited this print statement to match the format of 
		# the example output
		print (str(ct) + "       " + line)
		lines.append(line)
	# print len(pos)
	undent = ""
	for i in pos[1:]:
		undent += "~"
	lines.append(undent)
	# print undent
	return lines


def main():
	"""main program for testing"""
	global debug
	ct = 0
	
	for opt in sys.argv[1:]:
		if opt[0] != "-": break
		ct = ct + 1
		if opt == "-d": debug = True
		
	if len(sys.argv) < 2+ct:
		print ("Usage:  %s filename" % sys.argv[0])
		return
	parse("".join(mklines(sys.argv[1+ct])))
	return


main()