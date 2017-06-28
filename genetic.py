from random import uniform
from random import randint
from random import sample
from copy import deepcopy
import mlp
import puzzle_2048 as pzl
import numpy as np

def binaryArrayToInt(bitlist):
	num = 0
	for bit in bitlist:
		num = (num << 1) | int(bit)
	return num

def evaluateMaxValAndScore(individual):
	game = evaluateOnce(individual)
	max_val = max([max(line) for line in game.game])
	max_val *= 10000000
	return max_val + game.score

def evaluateMaxVal(individual):
	game = evaluateOnce(individual)
	return max([max(line) for line in game.game])

def evaluateScore(individual):
	return evaluateOnce(individual).score

def evaluate(individual, evaluation_function, num_evaluations):
	score = 0
	for i in range(num_evaluations):
		score += evaluation_function(individual)
	score /= num_evaluations
	return score

def evaluateOnce(individual):
	game = pzl.Puzzle2048()
	
	funcs = [game.up, game.down, game.left, game.right]
	
	arr = np.asarray(game.toArray())
	arr_max = arr.max()
	if arr_max:
		arr = arr / arr_max
	
	_, _, out, _ = individual.feed_forward(arr)
	move = binaryArrayToInt(out.round())
	moved = funcs[move]()
	while(moved and game.addNewNumber()):
		arr = np.asarray(game.toArray())
		arr_max = arr.max()
		if arr_max:
			arr = arr / arr_max
		
		_, _, out, _ = individual.feed_forward(arr)
		move = binaryArrayToInt(out.round())
		moved = funcs[move]()
	
	return game

def doCrossoverOnAttribute(mlp1, mlp2, child1, child2, attribute_weights, attribute_bias, max_cuts):
	#Preparing layer for cromosomal cut
	l_1 = np.concatenate((getattr(mlp1, attribute_weights), getattr(mlp1, attribute_bias)), axis=1)
	l_2 = np.concatenate((getattr(mlp2, attribute_weights), getattr(mlp2, attribute_bias)), axis=1)
	
	l_shape = l_1.shape
	
	l_1 = l_1.reshape((l_shape[0]*l_shape[1], 1))
	l_2 = l_2.reshape((l_shape[0]*l_shape[1], 1))
	
	#Turned layer into single array.
	#We are now ready to make the cuts
	num_cuts = randint(1, max_cuts)
	cut_locations = [0] + sorted(sample(range(1, l_1.shape[0]), num_cuts)) + [l_1.shape[0]]
	
	for i in range(1, len(cut_locations)):
		l_1[cut_locations[i-1]:cut_locations[i]], l_2[cut_locations[i-1]:cut_locations[i]] = l_2[cut_locations[i-1]:cut_locations[i]], l_1[cut_locations[i-1]:cut_locations[i]]
	
	#pass from chromosome back to mlp
	l_1 = l_1.reshape(l_shape)
	l_2 = l_2.reshape(l_shape)
	
	l_w_1 = l_1[0:l_shape[0], 0: l_shape[1] - 1]
	l_b_1 = l_1[0:l_shape[0], l_shape[1] - 1]
	l_b_1 = l_b_1.reshape((l_b_1.shape[0], 1))
	
	l_w_2 = l_2[0:l_shape[0], 0: l_shape[1] - 1]
	l_b_2 = l_2[0:l_shape[0], l_shape[1] - 1]
	l_b_2 = l_b_2.reshape((l_b_2.shape[0], 1))
	
	setattr(child1, attribute_weights, l_w_1)
	setattr(child1, attribute_bias, l_b_1)
	setattr(child2, attribute_weights, l_w_2)
	setattr(child2, attribute_bias, l_b_2)
	
	return child1, child2

def doCrossover(mlp1, mlp2, max_cuts=3):
	child1 = mlp.MLP(mlp1.input_layer_neurons, mlp1.hidden_layer_neurons, mlp1.output_layer_neurons)
	child2 = mlp.MLP(mlp1.input_layer_neurons, mlp1.hidden_layer_neurons, mlp1.output_layer_neurons)
	
	child1, child2 = doCrossoverOnAttribute(mlp1, mlp2, child1, child2, "hidden_layer_weights", "hidden_layer_bias", max_cuts)
	child1, child2 = doCrossoverOnAttribute(mlp1, mlp2, child1, child2, "output_layer_weights", "output_layer_bias", max_cuts)
	
	return child1, child2
	
def doMutationOnAttribute(mlp1, child, attribute_weights, attribute_bias, max_mutations):
	#Preparing layer for cromosomal mutation
	layer = np.concatenate((getattr(mlp1, attribute_weights), getattr(mlp1, attribute_bias)), axis=1)
	layer_shape = layer.shape
	layer = layer.reshape((layer_shape[0] * layer_shape[1], 1))
	
	num_muts = randint(1, max_cuts)
	for i in range(num_muts):
		swap = sample(range(0, layer.shape[0]), 2)
		layer[swap[0]], layer[swap[1]] = layer[swap[1]], layer[swap[0]]
		
	#pass from chromosome back to mlp
	layer = layer.reshape(layer_shape)
	
	layer_w = layer[0:layer_shape[0], 0: layer_shape[1] - 1]
	layer_b = layer[0:layer_shape[0], layer_shape[1] - 1]
	layer_b = layer_b.reshape((layer_b.shape[0], 1))
	
	setattr(child, attribute_weights, layer_w)
	setattr(child, attribute_bias, layer_b)
	
	return child

def doMutation(mlp1, max_mutations=3):
	child = mlp.MLP(mlp1.input_layer_neurons, mlp1.hidden_layer_neurons, mlp1.output_layer_neurons)
	child = doMutationOnAttribute(mlp1, child, "hidden_layer_weights", "hidden_layer_bias", max_mutations)
	child = doMutationOnAttribute(mlp1, child, "output_layer_weights", "output_layer_bias", max_mutations)
	return child

size_population = 100
generations = 100
mutation_probablility = 0.2
size_of_sample = 10
max_cuts = 10
max_mutations = 20
evaluation_function = evaluateMaxValAndScore
num_evaluations = 10

population = []
for i in range(size_population):
	population.append(mlp.MLP(16, 8, 2))

evaluation = list(map(lambda e: evaluate(e, evaluation_function, num_evaluations), population))

order = list(reversed(np.argsort(evaluation)))

population = [population[i] for i in order]
evaluation = [evaluation[i] for i in order]

for current_generation in range(generations):
	print("generation", current_generation)
	
	zipping = list(zip(evaluation, population))
	
	children = []
	while len(children) < size_population:
		genetic_operation = uniform(0, 1)
		if genetic_operation > mutation_probablility:
			#select parents
			s = sample(zipping, 5)
			s = sorted(s, key= lambda e: e[0])
			p1 = s[0][1]
			p2 = s[1][1]
			#do crossover
			c1, c2 = doCrossover(p1, p2, max_cuts)
			#create children
			children.append(c1)
			children.append(c2)
		else:
			#select parent
			s = sample(zipping, 5)
			s = sorted(s, key= lambda e: e[0])
			p1 = s[0][1]
			#do mutation
			c1 = doMutation(p1, max_mutations)
			children.append(c1)
	
	population = population + children
	evaluation = evaluation + list(map(lambda e: evaluate(e, evaluation_function, num_evaluations), children))
	
	order = list(reversed(np.argsort(evaluation)))[:size_population]
	
	population = [population[i] for i in order]
	evaluation = [evaluation[i] for i in order]
	
	print(evaluation)
	
print(evaluate(population[0]).game)


