from random import randint
import numpy as np


class Puzzle2048(object):
    def __init__(self, size=4, num_starting_squares=2):
        self.game = []
        self.score = 0

        for i in range(size):
            self.game += [[0]*size]

        for i in range(num_starting_squares):
            self.addNewNumber()

    # Merges values towards the left
    def merge(self):
        ans = False
        for i in range(len(self.game)):
            for j in range(1, len(self.game[0])):
                if self.game[i][j-1] == self.game[i][j] and self.game[i][j] != 0:
                    self.game[i][j-1] *= 2
                    self.game[i][j] = 0
                    self.score += self.game[i][j-1]
                    ans = True
        return ans

    # Makes the movement to the left
    def makeFall(self):
        was_valid = False
        for n in range(len(self.game[0])):
            for i in range(len(self.game)):
                for j in range(1, len(self.game[0])):
                    if self.game[i][j-1] == 0 and self.game[i][j] != 0:
                        self.game[i][j-1] = self.game[i][j]
                        self.game[i][j] = 0
                        was_valid = True
        return was_valid

    def rotateMatrixClockwise(self, matrix):
        matrix = list(zip(*matrix[::-1]))
        matrix = [list(line) for line in matrix]
        return matrix

    def rotateMatrixAntiClockwise(self, matrix):
        matrix = list(reversed(list(zip(*matrix))))
        matrix = [list(line) for line in matrix]
        return matrix

    def up(self):
        self.game = self.rotateMatrixAntiClockwise(self.game)
        ans = self.merge()
        ans = ans or self.makeFall()
        self.game = self.rotateMatrixClockwise(self.game)
        return ans

    def down(self):
        self.game = self.rotateMatrixClockwise(self.game)
        ans = self.merge()
        ans = ans or self.makeFall()
        self.game = self.rotateMatrixAntiClockwise(self.game)
        return ans

    def left(self):
        ans = self.merge()
        ans = ans or self.makeFall()
        return ans

    def right(self):
        self.game = self.rotateMatrixClockwise(self.game)
        self.game = self.rotateMatrixClockwise(self.game)
        ans = self.merge()
        ans = ans or self.makeFall()
        self.game = self.rotateMatrixClockwise(self.game)
        self.game = self.rotateMatrixClockwise(self.game)
        return ans

    def addNewNumber(self):
        freeSpots = []
        for i in range(len(self.game)):
            for j in range(len(self.game[0])):
                if self.game[i][j] == 0:
                    freeSpots += [(i, j)]

        if len(freeSpots) == 0:
            return False

        pickedSpot = freeSpots[randint(0, len(freeSpots) - 1)]
        # Add new number to matrix
        # With 10% chance of it being a 4
        if randint(0, 9) == 0:
            self.game[pickedSpot[0]][pickedSpot[1]] = 4
        else:
            self.game[pickedSpot[0]][pickedSpot[1]] = 2

        return True

    def toArray(self):
        ans = []
        for aux in self.game:
            ans += aux
        return ans


def doMove(game, num):
    if num == 0:
        return game.up()
    elif num == 1:
        return game.right()
    elif num == 2:
        return game.down()
    elif num == 3:
        return game.left()


if __name__ == '__main__':
    n = 100
    tot = 0
    curr_max = 0
    for i in range(n):
        game = Puzzle2048()
        doRandomMove(game)
        while(game.addNewNumber()):
            doRandomMove(game)
        tot += game.score

        max_val = max([max(l) for l in game.game])
        if max_val > curr_max:
            curr_max = max_val

    print(tot/n)
    print(curr_max)
