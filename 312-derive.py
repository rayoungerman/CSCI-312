#Jill Mao -  and Rebecca Youngerman - 930921312

#Read the length N from the command argument (or from input).
# Text file input from command line
length_n = int(input("Length? "))

#to use python version 2, as on lab computers, change to raw_input
filename = input("Fliename: ")

#Read and store all the productions.
dictionary = {} 
worklist = [] 

openfile = open(filename)

first = True

for line in openfile:
	
	if first == True:
		#get derive symbol and start symbol in first line
		productions = line.strip().split()
		deriveSym = " " + productions[1] + " "
		worklist.append(productions[0])
		first = False

	half = line.strip().split(deriveSym)
	key = half[0] #lhs
	values = half[1] #rhs
	
	#add values if the key is already there
	if key in dictionary:
		dictionary[key].append(values)
	
	#make new key for new nonterminals	
	else:
		dictionary[key] = [values]
	    
openfile.close()    
	
#While the worklist is not empty:
while len(worklist) != 0:
  
	#Get and delete one potential sentence s from the worklist.
	terminal = ""
	s = worklist.pop(0)
	sentence = s.split()
	
	
	#If the | s | > N, continue.
	if len(sentence) > length_n:
		continue
	
	

	#If s has no nonterminals, print s and continue.
	for index in range (len(sentence)):
		
		if sentence[index] not in dictionary:
			terminal += sentence[index] + ' '
			index += 1
		
			if index == len(sentence):
				print (terminal)
	
		#Sentence in dictionary; nonterminal
		else:
			
			#Replace NT in s with rhs; call it tmp.
			for sym in dictionary[sentence[index]]:
				tmp = terminal + sym + ' '
				
				for i in range (index + 1, len(sentence)):
					tmp += sentence[i] + ' '
					
				#Store tmp on worklist.    
				worklist.append(tmp)				
			break
			

				