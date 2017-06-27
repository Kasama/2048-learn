import copy
from random import randint

#Merges values towards the left
def merge(game):
	game = copy.deepcopy(game)
	for i in range(len(game)):
		for j in range(1, len(game[0])):
			if game[i][j-1] == game[i][j]:
				game[i][j-1] *= 2
				game[i][j] = 0
	return game

#Makes the movement to the left 
def makeFall(game):
	game = copy.deepcopy(game)
	for n in range(len(game[0])):
		for i in range(len(game)):
			for j in range(1, len(game[0])):
				if game[i][j-1] == 0:
					game[i][j-1] = game[i][j]
					game[i][j] = 0
	return game

def rotateMatrixClockwise(matrix):
	matrix = list(zip(*matrix[::-1]))
	matrix = [list(line) for line in matrix]
	return matrix
	
def rotateMatrixAntiClockwise(matrix):
	matrix = list(reversed(list(zip(*matrix))))
	matrix = [list(line) for line in matrix]
	return matrix

def up(game):
	game = rotateMatrixAntiClockwise(game)
	game = merge(game)
	game = makeFall(game)
	game = rotateMatrixClockwise(game)
	return game
	
def down(game):
	game = rotateMatrixClockwise(game)
	game = merge(game)
	game = makeFall(game)
	game = rotateMatrixAntiClockwise(game)
	return game
	
def left(game):
	game = merge(game)
	game = makeFall(game)
	return game
	
def right(game):
	game = rotateMatrixClockwise(game)
	game = rotateMatrixClockwise(game)
	game = merge(game)
	game = makeFall(game)
	game = rotateMatrixClockwise(game)
	game = rotateMatrixClockwise(game)
	return game

def addNewNumber(game):
	game = copy.deepcopy(game)
	
	freeSpots = []
	for i in range(len(game)):
		for j in range(len(game[0])):
			if game[i][j] == 0:
				freeSpots += [(i, j)]
	
	if len(freeSpots) == 0:
		return game, False
	
	pickedSpot = freeSpots[randint(0, len(freeSpots) - 1)]
	#Add new number to matrix
	#With 10% chance of it being a 4
	if randint(0, 9) == 0:
		game[pickedSpot[0]][pickedSpot[1]] = 4
	else:
		game[pickedSpot[0]][pickedSpot[1]] = 2
		
	return game, True

def printMatrix(matrix):
	for line in matrix:
		print(line)

