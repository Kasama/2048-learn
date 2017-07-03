from random import uniform
from random import randint
from random import sample
from random import getrandbits
import mlp
import puzzle_2048 as pzl
import numpy as np

def binaryArrayToInt(bitlist):
    num = 0
    for bit in bitlist:
        num = (num << 1) | int(bit)
    return num
    
def probabilityArrayToInt(problist):
    problist = np.asarray(problist)
    return np.argmax(problist)

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
    #print("evaluation")
    score = 0
    for i in range(num_evaluations):
        score += evaluation_function(individual)
    score /= num_evaluations
    return score

def evaluateOnce(individual):
    game = pzl.Puzzle2048()
    
    funcs = [game.up, game.right, game.down, game.left]
    
    arr = np.asarray(game.toArray())
    arr[arr > 0] = np.log2(arr[arr>0])
    arr_max = arr.max()
    if arr_max:
        arr = arr / arr_max
    
    _, _, out, _ = individual.feed_forward(arr) #(0.45, 0.6, 0.1, 0.3)
    move = probabilityArrayToInt(out)
    
    moved = False
    i = 0
    while not moved and i < len(funcs):
        moved = funcs[(move + i) % len(funcs)]()
        i += 1
    
    while(moved and game.addNewNumber()):
        arr = np.asarray(game.toArray())
        arr[arr > 0] = np.log2(arr[arr > 0])
        arr_max = arr.max()
        if arr_max:
            arr = arr / arr_max
        
        _, _, out, _ = individual.feed_forward(arr)
        move = probabilityArrayToInt(out)
        
        moved = False
        i = 0
        while not moved and i < len(funcs):
            moved = funcs[(move + i) % len(funcs)]()
            i += 1
    
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
    
    #Do the crossover
    for i in range(1, len(cut_locations)):
        if bool(getrandbits(1)):
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

size_population = 50
generations = 200
mutation_probablility = 0.2
size_of_sample = 10
max_cuts = 10
max_mutations = 20
evaluation_function = evaluateMaxValAndScore
num_evaluations = 10

population = []
for i in range(size_population):
    population.append(mlp.MLP(16, 8, 4))

evaluation = list(map(lambda e: evaluate(e, evaluation_function, num_evaluations), population))

order = list(reversed(np.argsort(evaluation)))[:size_population]

population = [population[i] for i in order]
evaluation = [evaluation[i] for i in order]

for current_generation in range(generations):
    print("generation", current_generation + 1)
    
    zipping = list(zip(evaluation, population))
    
    children = []
    while len(children) < size_population:
        genetic_operation = uniform(0, 1)
        if genetic_operation > mutation_probablility:
            #select parents
            s = sample(zipping, size_of_sample)
            s = sorted(s, key= lambda e: e[0])
            p1 = s[0][1]
            p2 = s[1][1]
            #do crossover
            c1, c2 = doCrossover(p1, p2, max_cuts)
            #create children
            children.append(c1)
            children.append(c2)
        else:
            a=2
            #select parent
            s = sample(zipping, size_of_sample)
            s = sorted(s, key= lambda e: e[0])
            p1 = s[0][1]
            #do mutation
            c1 = doMutation(p1, max_mutations)
            children.append(c1)
    
    #we also throw in a few new random ones for good measure
    children = children + [mlp.MLP(16, 8, 4)]*10
    
    #add children to the population
    population = population + children
    
    #evaluate new ones
    evaluation = evaluation + list(map(lambda e: evaluate(e, evaluation_function, num_evaluations), children))
    
    #get the size_population best results
    order = list(reversed(np.argsort(evaluation)))[:size_population]
    
    population = [population[i] for i in order]
    evaluation = [evaluation[i] for i in order]
    
    eval_to_print = []
    for num in evaluation:
        max_val = int(np.round(num/10000000))
        score_val = int(np.floor(num)%100000)
        eval_to_print.append((num, max_val, score_val))
    
    #val = n * 10000000 + game.score
    i = 0
    while i < len(eval_to_print):
        num = eval_to_print[i]
        print("(%f, %04d, %05d) " % num, end="")
        i += 1
        if not i % 4:
            print()
    print()
    #print(eval_to_print)
    #print(evaluation)

print("Generations Done!")
for i in range(20):
    print(evaluateOnce(population[0]).game)


