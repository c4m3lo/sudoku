class Grid(object):
    def __init__(self, sudoku):
        self.coords = [(r,c) for r in range(1,10) for c in range(1,10)]
        rows = [{(r,c) for c in range(1,10)} for r in range(1,10)]
        cols = [{(r,c) for r in range(1,10)} for c in range(1,10)]
        squares = [{(bigr*3+r, bigc*3+c) for r in range(1,4) for c in range(1,4)} for bigr in range(0,3) for bigc in range(0,3)]
        self.all_groups = rows + cols + squares
        self.groups = {coord:[g for g in self.all_groups if coord in g] for coord in self.coords}

        self.start = {coord: False for coord in self.coords}
        # sudoku is a string of nine rows of nine chars
        # each char should be a digit or space
        row = 1
        col = 1
        for c in sudoku:
            if c == '\n':
                row += 1
                col = 1
            elif c == ' ':
                col += 1
            else:
                self.start[(row, col)]=int(c)
                col += 1

    def set_complements(self):
        row_trios = [((r,bigc*3+1), (r,bigc*3+2), (r,bigc*3+3)) for bigc in range(0,3) for r in range(1,10)]
        col_trios = [((bigr*3+1,c), (bigr*3+2,c), (bigr*3+3,c)) for bigr in range(0,3) for c in range(1,10)]
        all_trios = row_trios + col_trios

        groups_for_trio = {trio: tuple(group for group in self.all_groups if set(trio) <= group) for trio in all_trios}

        self.complements = dict([])
        for trio in groups_for_trio:
            sixer = [tuple(groups_for_trio[trio][index] - set(trio)) for index in (0,1)]
            self.complements[sixer[0]] = sixer[1]
            self.complements[sixer[1]] = sixer[0]

    def place(self, answer, coord):
        for remove in self.options[coord] - {answer}:
            self.remove_option(coord, remove)

    def remove_option(self, coord, remove):
        self.options[coord] -= {remove}
        self.check_for_complete_groups(coord, remove)
        self.check_for_complements(coord, remove)
        self.check_for_clusters(coord)

    def check_for_complete_groups(self, coord, removed):
        for group in self.groups[coord]:
            other_places_in_group = [gr_coord for gr_coord in group if removed in self.options[gr_coord]]
            if len(other_places_in_group) == 1:
                self.place(removed, list(other_places_in_group)[0])

    def check_for_complements(self, coord, removed):
        sixes = [six for six in self.complements if coord in six]
        for six in sixes:
            if len([1 for six_coord in six if removed in self.options[six_coord]]) == 0:
                # So this number (removed) is not in this block of 6 squares.
                # Therefore it must be in the other three squares of the group.
                # Therefore it must not be in the complementary six
                for ko_coord in self.complements[six]:
                    if removed in self.options[ko_coord]:
                        self.remove_option(ko_coord, removed)

    def check_for_clusters(self, coord):
        check_for = self.options[coord]
        for group in self.groups[coord]:
            cluster = {group_coord for group_coord in group if self.options[group_coord] <= check_for}
            if len(cluster) == len(check_for):
                for remove_coord in group - cluster:
                    for remove in check_for & self.options[remove_coord]:
                        self.remove_option(remove_coord, remove)

    def follow_rules(self):
        self.set_complements()
        self.options = {coord:set(range(1,10)) for coord in self.coords}

        for coord in self.coords:
            if self.start[coord]:
                self.place(self.start[coord], coord)

    def valid(self):
        for group in self.all_groups:
            for digit in range(1,10):
                if len([1 for coord in group if self.grid[coord] == digit]) > 1:
                    return False
        return True

    def brute_force(self):
        self.grid = self.start.copy()
        pos = 0
        digit = 1
        while pos < len(self.coords):
            self.grid[self.coords[pos]] = digit
            if self.valid():
                pos += 1
                while pos < len(self.coords) and self.start[self.coords[pos]]:
                    pos += 1
                digit = 1
            else:
                while digit == 9:
                    self.grid[self.coords[pos]] = False
                    pos -= 1
                    while self.start[self.coords[pos]]:
                        pos -= 1
                    digit = self.grid[self.coords[pos]]
                digit += 1

    def pretty_options(self):
        response = "#=====+=====+=====#=====+=====+=====#=====+=====+=====#\n"
        for r in range(1,10):
            for line in range(0,3):
                response += "#"
                for c in range(1,10):
                    response += ' '
                    for o in range(1,4):
                        check = line*3+o
                        if check in self.options[(r,c)]:
                            response += str(check)
                        else:
                            response += " "
                    if c%3==0:
                        response+= " #"
                    else:
                        response += " |"
                response += "\n"
            if r%3 == 0:
                response += "#=====+=====+=====#=====+=====+=====#=====+=====+=====#\n"
            else:
                response += "+-----+-----+-----+-----+-----+-----+-----+-----+-----+\n"
        return response

    def pretty_grid(self):
        return '\n'.join([''.join([self.display_char((row, col)) for col in range(1,10)]) for row in range(1,10)])

    def display_char(self,coord):
        if self.grid[coord]:
            return str(self.grid[coord])
        else:
            return ' '

    def recursion(self):
        self.options = {coord:set(range(1,10)) for coord in self.coords}

        for coord in self.coords:
            if self.start[coord]:
                self.place(self.start[coord], coord)

    def knockout(self, coord):
        assert len(self.options[coord]) == 1
        answer = list(self.options[coord])[0]
        ko_coords = set.union(*self.groups[coord]) - {coord}
        for ko_coord in ko_coords:
            if answer in self.options[ko_coord]:
                if len(self.options[ko_coord]) == 1:
                    return False
                self.options[ko_coord] -= {answer}
                

fiendish = Grid(' 25   8  \n'
              '   15   4\n'
              '4   8   9\n'
              '       6 \n'
              ' 46 3 58 \n'
              ' 8       \n'
              '7   4   1\n'
              '2   19   \n'
              '  9   42 ')


import time
start = time.clock()
fiendish.follow_rules()
print(time.clock()-start)
print(fiendish.pretty_options())

start = time.clock()
fiendish.brute_force()
print(time.clock()-start)
print(fiendish.pretty_grid())

fiendish.recursion()


# fiendish.brute_force
#
# fiendish2 = Grid()
# fiendish2.follow_rules('1   5   2\n'
#               '  4 138  \n'
#               ' 9     6 \n'
#               ' 6       \n'
#               '53  2  71\n'
#               '       4 \n'
#               ' 7     2 \n'
#               '  917 3  \n'
#               '3   8   4')
# print(fiendish2)
#
