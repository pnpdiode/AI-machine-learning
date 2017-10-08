from Tkinter import *
import pandas as pd
import numpy as np
import time

#Globals*******************************************************************************************
#Window Size
Width = 500
Height = 500
GAMMA = 0.9
EPSILON = 0.9
LearningRate = 0.1
EPISODES=100
ACTIONS = ["right","left","up","down"]
Q = pd.DataFrame(np.zeros((25,4)),columns=ACTIONS)
          
path = [[1,0,1,1,0],
		[1,1,1,1,1],
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

def ChooseAction(state):
	if(Q.iloc[state].all() == 0):
		return(np.random.choice(ACTIONS))
	return(Q.iloc[state].idxmax())

def GetFeedback(path,Circle):
	x = Circle.Position.Y//100
	y = Circle.Position.X//100
	reward = path[x][y]
	state = x*5 + y
	if(reward == 20):
		reward = 2
	elif(reward == 0):
		reward = -1
	else:
		reward = 0
	
	return(state,reward)
	 
def ReachedGoal(path,Circle):
	x = Circle.Position.Y//100
	y = Circle.Position.X//100
	if(path[x][y] == 20):
		return(True)
	return(False)

def Punish(Circle):
	x = Circle.Position.Y//100
	y = Circle.Position.X//100
	if(path[x][y] == 0):
		return(True)
	return(False)
	
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
	Canvas.InitCanvas(Width,Height)
	
	colors = ["red","black","yellow","cyan","magenta"]
	
	DrawPath(Canvas,path)
	hell = 0
	while(EPISODES != 0):
		Circle = CircleProperties(50,50,25,"red")
		#State = ChooseState(path)
		State = 0
		Circle,Success = Move(Canvas,Circle,"na")
		Steps = 0
		Canvas.Update()
		while (not ReachedGoal(path,Circle)):
			Action = ChooseAction(State)
			
			Circle,Success = Move(Canvas,Circle,Action)
			if(Success):
				NextState, Reward = GetFeedback(path,Circle)
				
				if(ReachedGoal(path,Circle)):
					QTarget = Reward
				else:
					QTarget = Reward + GAMMA*Q.iloc[NextState].max()
				Q.iloc[State][Action] += LearningRate*(QTarget - Q.iloc[State][Action])
				State = NextState
				Steps += 1
				Canvas.Update()
				if(Punish(Circle)):
					Circle.Clear(Canvas)
					Circle = CircleProperties(50,50,25,"red")
					#State = ChooseState(path)
					State = 0
					Circle,Success = Move(Canvas,Circle,"na")
					Steps = 0
					hell += 1
					Canvas.Update()
					print "in hell ",hell
			else:
				Q.iloc[State][Action] = -10
			time.sleep(0.3)
		#time.sleep(1)
		Circle.Clear(Canvas)
		EPISODES -= 1
	print(Q)
	while(True):
		Action = raw_input()
		if(ACTIONS == 'q'):
			break
		Move(Canvas,Circle,Action)
	
if __name__ == "__main__":
	main()
	
	
	
	
	
	

