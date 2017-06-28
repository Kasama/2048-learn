import puzzle_2048 as pzl
import numpy as np
from copy import deepcopy


class Node:
    def __init__(self, game: pzl.Puzzle2048, probability: float):
        self.game = game
        self.accumulated_prob = probability
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
            every_move.append(child)
    # end for
    if len(every_move) == 0:
        return []
    movement_prob = 1 / len(every_move)
    next_step = []
    for move in every_move:
        free_spots = move.getFreeSpots()
        spot_prob = 1 / len(free_spots)
        for spot in free_spots:
            for num in [(2, 0.9), (4, 0.1)]:
                n = num[0]
                # parent node probability * movement probability *
                # spot probability * number probability
                prob = node.accumulated_prob * \
                    movement_prob * \
                    spot_prob * \
                    num[1]
                new_game = deepcopy(move)
                new_game.addNumber(spot, n)
                new_move = Node(new_game, prob)
                next_step.append(new_move)
            # end for
        # end for
    # end for
    return next_step
# end genNextStep


start = Node(pzl.Puzzle2048(4, 1), 1)
print('start member:', start)
second = genNextStep(start)
print('second:', second)
total = 0
for node in second:
    total += node.accumulated_prob
print('total probability:', total)
