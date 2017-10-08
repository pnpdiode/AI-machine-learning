from Tkinter import *
import pandas as pd
import numpy as np
import time

#Globals*******************************************************************************************
#Window Size
Width = 500
Height = 500
GAMMA = 0.9 #discountfactor
EPSILON = 0.9
LearningRate = 0.5#learning rate
EPISODES=100
ACTIONS = ["right","left","up","down"]#possible actions
Q = pd.DataFrame(np.zeros((25,4)),columns=ACTIONS)#create Q table
 
#Maze to Create. 0->BlackBox 20->Goal          
path = [[1,1,1,1,1],
		[1,0,0,1,1],
		[1,1,0,1,1],
		[1,0,20,0,1],
		[1,1,1,1,1]]

#Classes*******************************************************************************************
class Position:
	def __init__(self,x,y):
		self.X = x
		self.Y = y
#Bounds
#  (UPX,UPY) -------------
#            |           |
#            |           |
#            -------------(LRX,LRY)   
class Bounds:
	def __init__(self,UPX,UPY,LRX,LRY):
		self.UPX = UPX
		self.UPY = UPY
		self.LRX = LRX
		self.LRY = LRY

class QLearning:
	Qtable = None
	def __init__(self,LearningRate,GAMMA,EPSILON):
		self.LearningRate = LearningRate
		self.GAMMA = GAMMA
		self.EPSILON = EPSILON
		
	def InitQtable(self,Rows,Columns):
		self.Qtable = pd.DataFrame(Rows,columns=Columns)
	
	def ChooseAction(self,State):
		if(self.Qtable.iloc[State].all() == 0):#if all 0 then choose randomly
			return(np.random.choice(list(self.Qtable)))
		return(self.Qtable.iloc[State].idxmax())#else return action with max value
	
	def Learn(self,CurrentState,CurrentAction,Reward,NextState,isReachedGoal):
		if(isReachedGoal):
			Qtarget = Reward
		else:
			Qtarget = Reward + self.GAMMA*self.Qtable.iloc[NextState].max()
			
		self.Qtable.iloc[CurrentState][CurrentAction] += self.LearningRate*(Qtarget - self.Qtable.iloc[CurrentState][CurrentAction])
		
	def AssignValue(self,State,Action,Value):
		self.Qtable.iloc[State][Action] = Value
	
	def PrintTable(self):
		print(self.Qtable)
		
class CanvasProperties:
	Canvas = None
	CanvasBounds = None
	def __init__(self,root):
		self.root = root
	
	def InitCanvas(self,Width,Height):
		self.Canvas = Canvas(self.root,width=Width,height=Height)
		self.Canvas.pack()
		self.CanvasBounds = Bounds(0,0,Width,Height)
	
	def Update(self):
		self.root.update_idletasks()
		self.root.update()
	
	def ClearObject(self,Object):
		self.Canvas.delete(Object)

		
class CircleProperties:
	CurrentlyDrawnCircle = None
	def __init__(self,LocX,LocY,InRadius,InColor):
		self.Position = Position(LocX,LocY)
		self.Radius = InRadius
		self.Color = InColor
		
	def GetDrawnCircle(self):
		return(self.CurrentlyDrawnCircle)
		
	def SetDrawnCircle(self,Current):
		self.CurrentlyDrawnCircle = Current
	
	def Clear(self,canvas):
		canvas.ClearObject(self.CurrentlyDrawnCircle)




#Functions*****************************************************************************************
#rendering functions
def DrawCircle(canvas,Circle):
	return(canvas.Canvas.create_oval(Circle.Position.X-Circle.Radius,Circle.Position.Y-Circle.Radius,\
	                   Circle.Position.X+Circle.Radius,Circle.Position.Y+Circle.Radius,\
	                   fill=Circle.Color))

def ClearCircle(canvas,Circle):
	canvas.ClearObject(Circle.GetDrawnCircle())
		
def Move(canvas,Circle,Action):
	if(Action == "up"):
		if(Circle.Position.Y-100 > canvas.CanvasBounds.UPY):
			ClearCircle(canvas,Circle)
			Circle.Position.Y -= 100
			Circle.SetDrawnCircle(DrawCircle(canvas,Circle))
		else:
			return(Circle,False)
	elif(Action == "down"):
		if(Circle.Position.Y+100 < canvas.CanvasBounds.LRY):
			ClearCircle(canvas,Circle)
			Circle.Position.Y += 100
			Circle.SetDrawnCircle(DrawCircle(canvas,Circle))
		else:
			return(Circle,False)		
	elif(Action == "right"):
		if(Circle.Position.X+100 < canvas.CanvasBounds.LRX):
			ClearCircle(canvas,Circle)
			Circle.Position.X += 100
			Circle.SetDrawnCircle(DrawCircle(canvas,Circle))
		else:
			return(Circle,False)
	elif(Action == "left"):
		if(Circle.Position.X-100 > canvas.CanvasBounds.UPX):
			ClearCircle(canvas,Circle)
			Circle.Position.X -= 100
			Circle.SetDrawnCircle(DrawCircle(canvas,Circle))
		else:
			return(Circle,False)
	else:
		ClearCircle(canvas,Circle)
		Circle.SetDrawnCircle(DrawCircle(canvas,Circle))
	return(Circle,True)

def drawLines(canvas,color):
	if(canvas.CanvasBounds.LRX < canvas.CanvasBounds.LRY):
		end = canvas.CanvasBounds.LRY
	else:
		end = canvas.CanvasBounds.LRX
	for X in range(100,end,100):
		canvas.Canvas.create_line(X,X-X,X,canvas.CanvasBounds.LRY,fill=color,width=3)
		canvas.Canvas.create_line(X-X,X,canvas.CanvasBounds.LRX,X,fill=color,width=3)
	return()
	
def DrawPath(canvas,path):
	colors = ["black","white","green"]
	for i in range(len(path)):
		for j in range(len(path)):
			if path[j][i] == 20:
				canvas.Canvas.create_rectangle(i*100+5,j*100+5,(i*100)+95,(j*100)+95,fill="green")
			elif path[j][i] == 0:
				canvas.Canvas.create_rectangle(i*100+5,j*100+5,(i*100)+95,(j*100)+95,fill="black")
	drawLines(canvas,"red")
	return()
######################################################################################################
#Learning related functions

#Choose action for given satte
def ChooseAction(state):
	if(Q.iloc[state].all() == 0):#if all 0 then choose randomly
		return(np.random.choice(ACTIONS))
	return(Q.iloc[state].idxmax())#else return action with max value

#get feedback from enviornment
def GetFeedback(path,Circle):
	x = Circle.Position.Y//100
	y = Circle.Position.X//100
	reward = path[x][y]#get reward from maze
	state = x*5 + y#get next state
	if(reward == 20):
		reward = 2
	elif(reward == 0):
		reward = -1
	else:
		reward = 0
	
	return(state,reward)

#Reached Goal?	 
def ReachedGoal(path,Circle):
	x = Circle.Position.Y//100
	y = Circle.Position.X//100
	if(path[x][y] == 20):
		return(True)
	return(False)

#Black Box?
def Punish(Circle):
	x = Circle.Position.Y//100
	y = Circle.Position.X//100
	if(path[x][y] == 0):
		return(True)
	return(False)

#Randomly choose state 	
def ChooseState(path):
	x = np.random.random_integers(0,4)
	y = np.random.random_integers(0,4)
	if(path[x][y] == 0 or path[x][y] == 20):
		ChooseState(path)
	return(path[x][y])


#Main**********************************************************************************************
def main():
	global EPISODES
	root = Tk()
	
	Width = 500
	Height = 500
	Canvas = CanvasProperties(root)
	Canvas.InitCanvas(Width,Height)#Create canvas
	
	colors = ["red","black","yellow","cyan","magenta"]
	
	debug = False
	Circle = CircleProperties(50,50,25,"red")#set circle properties
	#State = ChooseState(path)
	State = 0
	Steps = 0
	DrawPath(Canvas,path)#draw maze
	
	Qlearner = QLearning(LearningRate,GAMMA,EPSILON)
	
	Qlearner.InitQtable(np.zeros((25,4)),ACTIONS)

	while(EPISODES != 0 and debug is False):
		Circle = CircleProperties(50,50,25,"red")
		#State = ChooseState(path)
		State = 0
		Steps = 0
		Circle,Success = Move(Canvas,Circle,"na")
		Canvas.Update()
		while (not ReachedGoal(path,Circle)):#while not at the goal
			Action = Qlearner.ChooseAction(State)#choose action
			
			Circle,Success = Move(Canvas,Circle,Action)
			
			#Was move successful?
			if(Success):
				NextState, Reward = GetFeedback(path,Circle)#get feedback
				
				#if reached goal
				if(ReachedGoal(path,Circle)):
					Qlearner.Learn(State,Action,Reward,NextState,True)
				#else find qtarget given reward and max value of the next state 	
				else:
					Qlearner.Learn(State,Action,Reward,NextState,False)
				
				State = NextState
				Steps += 1
				Canvas.Update()
				if(Punish(Circle)):#if in blackbox then reset
					time.sleep(0.01)
					Circle.Clear(Canvas)
					Circle = CircleProperties(50,50,25,"red")
					State = 0
					Circle,Success = Move(Canvas,Circle,"na")
					Steps = 0
					Canvas.Update()
			else:#if not then respective action is not possible for the current state
				Qlearner.AssignValue(State,Action,-10)#prevent taking this action in future
			
			time.sleep(0.001)
		
		Circle.Clear(Canvas)
		EPISODES -= 1
	
	#debug
	while(debug):
		Action = raw_input()
		if(ACTIONS == 'q'):
			break
		Move(Canvas,Circle,Action)
	Qlearner.PrintTable()

	
if __name__ == "__main__":
	main()
	
	
	
	
	
	

