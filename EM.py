import numpy as np
import puzzle_2048 as pzl
from copy import deepcopy


class Inversions:  # {
    def __init__(self):
        self.inv_count = 0

    # checks how ordered is the array `x`. 1 is fully ordered and 0 is random
    # fully ordered can be in crescent or decreasing order
    @classmethod
    def ratio(klass, x):
        max_inv = (len(x) * (len(x) - 1)) / 2
        # -0.5 <= x <= 0.5
        x = (klass().count_inversions(x).inv_count / max_inv) - 0.5
        return (x ** 2) * 4

    def count_inversions(self, x):  # {
        midsection = int(len(x) / 2)
        a = x[:midsection]
        b = x[midsection:]
        if len(x) > 1:
            self.count_inversions(a)
            self.count_inversions(b)
            i, j = 0, 0
            for k in range(len(a) + len(b) + 1):
                if a[i] <= b[j]:
                    x[k] = a[i]
                    i += 1
                    if i == len(a) and j != len(b):
                        while j != len(b):
                            k += 1
                            x[k] = b[j]
                            j += 1
                        break
                elif a[i] > b[j]:
                    x[k] = b[j]
                    self.inv_count += (len(a) - i)
                    j += 1
                    if j == len(b) and i != len(a):
                        while i != len(a):
                            k += 1
                            x[k] = a[i]
                            i += 1
                        break
                # end if
            # end for
        # end if
        return self
    # end count_inversion }
# end Inversion }


def find_best_move(game: pzl.Puzzle2048, acc_prob=1, lookahead: int=2):  # {
    move_scores = [0, 0, 0, 0]
    # 0 - up | 1 - right | 2 - down | 3 - left
    for move in [0, 1, 2, 3]:
        game_copy = deepcopy(game)
        if pzl.doMove(game_copy, move):
            free_spots = game_copy.getFreeSpots()
            spot_prob = 1 / 16
            for spot in free_spots:
                for num in [(2, 0.9), (4, 0.1)]:
                    game_copy.addNumber(spot, num[0])
                    prob = 0.25 * spot_prob * num[1] * acc_prob
                    if lookahead > 1:
                        score, _ = find_best_move(game_copy, prob, lookahead-1)
                    else:
                        max_tile = max([max(line) for line in game.game])

                        # table = np.asarray(game.game)
                        # line = [Inversions.ratio(l) for l in table]
                        # row = [Inversions.ratio(r) for r in table.T]
                        # inv = sum(line) + sum(row) / (len(line) + len(row))

                        score = \
                            game_copy.score + \
                            (max_tile * 1_000_000)
                        # (inv * 100_000_000)
                    # end if
                    move_scores[move] += prob * score
                # end for
            # end for
        # end if
    # end for
    best_move = 0
    best_score = 0
    for move in [0, 1, 2, 3]:
        if move_scores[move] > best_score:
            best_move = move
            best_score = move_scores[move]
    return (best_score, best_move)
# end find_best_move }


game = pzl.Puzzle2048(4, 2)
# game.game.game = [
#         [2, 0, 0, 0],
#         [2, 0, 0, 0],
#         [0, 0, 0, 0],
#         [16, 2, 4, 0]]
#
game.game = \
        [[16, 128, 8, 2], [4, 32, 512, 16], [2, 64, 1024, 32], [0, 32, 128, 4]]

names = ['up', 'right', 'down', 'left']
while (True):
    best_score, move = find_best_move(game, 1, 4)
    print('got best score:', best_score, 'move:', move)

    if(not pzl.doMove(game, move)):
        print('game over. Score:', game.score)
        break
    game.addNewNumber()

    print('moving', names[move])
    print('score:', game.score)
    print('game:\n' + str(np.array(game.game)))
