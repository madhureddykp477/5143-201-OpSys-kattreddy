import threading
from commandsFile import commandsClass

class commandSplitter(object):
	def __init__(self):
		self.splitCommand=[]
	
	def split(self,command):
		#split passed command based on space
		self.splitCommand = command.split(" ")
		return self.splitCommand

#command checker inherits from command splitter
class commandChecker(commandSplitter):
	def __init__(self):
		self.userCommand = None
		self.splitCommand = None
		self.commandLength= None
		self.mainCommand = None
		self.lastParameter= ""
		self.commandThread= None
		self.daemonStatus= False;
		self.commandList = ["ls","cat","cd","cp", "wc", "rm", "mkdir", "pwd", "head", "tail", "grep"]
	
	#function that accepts command for the program
	def acceptCommand(self, command):
		self.userCommand = command
		self.processComand()
	
	# function that starts processing of accepted command
	# splits the command and gets the length
	# Gets the main command without flags
	def processComand(self):
		self.splitCommand = self.split(self.userCommand)
		self.commandLength = len(self.splitCommand)
		self.mainCommand = self.splitCommand[0]
		
		# get last parameter to check if it is an &
		if self.commandLength > 1:
			self.lastParameter = self.splitCommand[self.commandLength-1]
			
		self.passCommand()
		
	def passCommand(self):
		# check if daemon thread is to be created
		if self.lastParameter=='&':
			self.daemonStatus = True
			
		#check if command is in list
		if self.mainCommand in self.commandList:
			#LS COMMAND
			if str.upper(self.mainCommand) == "LS":
				self.thread_t = threading.Thread(target=commandsClass.ls, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
			
			#CAT COMMAND
			elif str.upper(self.mainCommand) == "CAT":
				self.thread_t = threading.Thread(target=commandsClass.cat, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
			#CD COMMAND
			elif str.upper(self.mainCommand) == "CD":
				self.thread_t = threading.Thread(target=commandsClass.cd, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
			#CP COMMAND
			elif str.upper(self.mainCommand) == "CP":
				self.thread_t = threading.Thread(target=commandsClass.cp, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
			#WC COMMAND
			elif str.upper(self.mainCommand) == "WC":
				self.thread_t = threading.Thread(target=commandsClass.wc, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
			
			#RM COMMAND
			elif str.upper(self.mainCommand) == "RM":
				self.thread_t = threading.Thread(target=commandsClass.rm, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
			#MKDIR COMMAND
			elif str.upper(self.mainCommand) == "MKDIR":
				self.thread_t = threading.Thread(target=commandsClass.mkdir, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
			
			#PWD COMMAND
			elif str.upper(self.mainCommand) == "MKDIR":
				self.thread_t = threading.Thread(target=commandsClass.pwd, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
			#HEAD COMMAND
			elif str.upper(self.mainCommand) == "MKDIR":
				self.thread_t = threading.Thread(target=commandsClass.head, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
			#TAIL COMMAND
			elif str.upper(self.mainCommand) == "MKDIR":
				self.thread_t = threading.Thread(target=commandsClass.tail, args=(self.splitCommand, self.commandLength))
				self.thread_t.daemon = self.daemonStatus
				self.thread_t.start()
				self.thread_t.join()
				
				

		#print an error message for wrong command entered
		else:
			if self.userCommand=="":
				pass
			else:
				print(" wrong command available commands are: ")
				print(self.commandList)

class shell(object):
	def __init__(self):
		self.command = commandChecker()
	
	def run(self):
		while True:
			#get userinput
			self.userInput = input("% ")
			
			
			#check user input for termination callable
			if str.upper(self.userInput) == "EXIT" or str.upper(self.userInput) =="close":
				exit()
			
			#call the accept command method
			else:
				self.command.acceptCommand(self.userInput)
	
	#function to exit shell
	def exit():
		raise SystemExit
		
class mainThread(object):
	def __init__(self):
		self.shellCall = shell()
		self.thread_t = None
		
	def run(self):
		self.thread_t = threading.Thread(target=self.shellCall.run)
		self.thread_t.start()
		self.thread_t.join()

if __name__ == '__main__':
	start = mainThread()
	start.run()

