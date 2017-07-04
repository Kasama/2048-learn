import numpy as np
import puzzle_2048 as pzl
from copy import deepcopy


class Node:
    def __init__(self, game: pzl.Puzzle2048, probability: float, move: int):
        self.game = game
        self.accumulated_prob = probability
        self.move = move
    # end init

    def __str__(self):
        return 'prob: ' + str(self.accumulated_prob) + \
                '\ngame:\n' + str(np.asarray(self.game.game))
    # end __str__

    def __repr__(self):
        return self.__str__()
    # end __repr__
# end Node


def genNextStep(node: Node):
    every_move = []
    # 0 - up | 1 - right | 2 - down | 3 - left
    for move in [0, 1, 2, 3]:
        child = deepcopy(node.game)
        if (pzl.doMove(child, move)):
            every_move.append((child, move))
    # end for
    if len(every_move) == 0:
        return []
    movement_prob = 1 / len(every_move)
    next_step = []
    for child in every_move:
        game = child[0]
        move = child[1]
        free_spots = game.getFreeSpots()
        # spot_prob = 1 / len(free_spots)
        spot_prob = 1 / 16  # maybe use 16, maybe use len(free_spots)
        for spot in free_spots:
            for num in [(2, 0.9), (4, 0.1)]:
                n = num[0]
                # parent node probability * movement probability *
                # spot probability * number probability
                prob = node.accumulated_prob * \
                    movement_prob * \
                    spot_prob * \
                    num[1]
                new_game = deepcopy(game)
                new_game.addNumber(spot, n)
                if node.move == -1:
                    new_move = Node(new_game, prob, move)
                else:
                    new_move = Node(new_game, prob, node.move)
                next_step.append(new_move)
            # end for
        # end for
    # end for
    return next_step
# end genNextStep


def predict(game, lookahead=1):
    prediction = genNextStep(game)
    for i in range(lookahead-1):
        future = []
        for node in prediction:
            future += genNextStep(node)
        prediction = future
    return prediction


num_tests = 10
max_val = 0
my_max_score = 0

for i in range(num_tests):
    start = Node(pzl.Puzzle2048(4, 2), 1, -1)

    while (True):
        second = predict(start, 2)

        max_node = None
        max_score = 0
        max_prob = 0
        for node in second:
            # max_tile = max([max(line) for line in node.game.game])
            # max_tile *= 10000000
            max_tile = 0
            score = node.accumulated_prob * (node.game.score + max_tile)
            # print('game score:', node.game.score, ' - score:', score)
            if score >= max_score:
                max_score = score
                max_node = node
                max_prob = node.accumulated_prob
            # end if
        # end for
        
        if not max_node:
            max_val += max(start.game.toArray())
            print(start.game.score)
            my_max_score += start.game.score
            break
        
        pzl.doMove(start.game, max_node.move)
        start.game.addNewNumber()

        #print('max possible score:', max_score/max_prob)
        #names = ['up', 'right', 'down', 'left']
        #print('moving', names[max_node.move])
        #print('score:', start.game.score)
        #print('game:\n' + str(np.array(start.game.game)))
    print(i)

print(max_val/num_tests, my_max_score/num_tests)