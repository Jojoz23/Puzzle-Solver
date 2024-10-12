import argparse
import sys
import copy

#====================================================================================

char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_2_by_2, is_single, coord_x, coord_y, orientation):
        """
        :param is_2_by_2: True if the piece is a 2x2 piece and False otherwise.
        :type is_2_by_2: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_2_by_2 = is_2_by_2
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation
        self.__set_type()
        self.h_value = 0

    def set_coords(self, coord_x, coord_y):
        """
        Move the piece to the new coordinates. 

        :param coord: The new coordinates after moving.
        :type coord: int
        """

        self.coord_x = coord_x
        self.coord_y = coord_y

    def __set_type(self):
        if self.is_2_by_2:
            self.type = "2x2"
        elif self.is_single:
            self.type = "1x1"
        elif self.orientation == 'h':
            self.type = "2x1"
        elif self.orientation == 'v':
            self.type = "1x2" 

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_2_by_2, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)        


class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, height, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = height
        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()

        self.blanks = []

        self.find_empty_spaces()

    # customized eq for object comparison.
    def __eq__(self, other):
        if isinstance(other, Board):
            return self.grid == other.grid
        return False

    def __hash__(self) -> int:
        return hash(grid_to_string(self.grid))

    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_2_by_2:
                self.grid[piece.coord_y][piece.coord_x] = '1'
                self.grid[piece.coord_y][piece.coord_x + 1] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def update_board(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                self.grid[y][x] = '.'

        for piece in self.pieces:
            if piece.is_2_by_2:
                self.grid[piece.coord_y][piece.coord_x] = '1'
                self.grid[piece.coord_y][piece.coord_x + 1] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'


    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()

    def find_empty_spaces(self):
        """
        Emptyspaces in grid

        """
        self.blanks = set() #change to set, or make it attribute

        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == '.':
                    self.blanks.add((x, y))
    
    def total_h(self):
        sum = 0
        for piece in self.pieces:
            sum += piece.h_value
        return sum
        

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, hfn, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param hfn: The heuristic function.
        :type hfn: Optional[Heuristic]
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.hfn = hfn
        self.f = f # maybe combine hfn and depth
        self.depth = depth
        self.parent = parent


class minHeap:
    def __init__(self) -> None:
        self.list = []
    def insert(self, board):
        self.list.append(board)
        self.bubble_up(len(self.list) - 1)

    def bubble_up(self, index):
        parent = self.get_parent_index(index)
        if index == 0 or self.list[parent].f <= self.list[index].f:
            return
        self.list[parent], self.list[index] = self.list[index], self.list[parent]
        self.bubble_up(parent)

    def extract_min(self):
        min_element = self.list[0]
        self.list[0] = self.list[-1]
        self.list.pop()
        self.bubble_down(0)
        return min_element
    
    def bubble_down(self, index):
        left_child = 2 * index + 1
        right_child = 2 * index + 2
        smallest = index

        if left_child < len(self.list) and self.list[left_child].f <= self.list[smallest].f:
            smallest = left_child
        
        if right_child < len(self.list) and self.list[right_child].f <= self.list[smallest].f:
            smallest = right_child
        
        if smallest != index:
            self.list[index], self.list[smallest] = self.list[smallest], self.list[index]
            self.bubble_down(smallest)


    def get_parent_index(self, index):
        return (index - 1) // 2
    
    def is_empty(self):
        return self.list == []

def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    final_pieces = []
    final = False
    found_2by2 = False
    finalfound_2by2 = False
    height_ = 0
    one_found = False
    skip_one_line = False

    for line in puzzle_file:
        height_ += 1
        if line == '\n':
            if not final:
                height_ = 0
                final = True
                line_index = 0
                one_found = False
                skip_one_line = False
            continue
        if not final: #initial board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1': # fix to include more than 1
                    if skip_one_line == False:
                        one_found = True
                        if found_2by2 == False:
                            pieces.append(Piece(True, False, x, line_index, None))
                            found_2by2 = True
                        elif found_2by2 == True:
                            found_2by2 = False
                elif ch == '\n':
                    if skip_one_line == False and one_found == True:
                        skip_one_line = True
                        one_found = False
                    elif skip_one_line == True:
                        skip_one_line = False
        else: #goal board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    final_pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    final_pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    final_pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1':
                    if skip_one_line == False:
                        one_found = True
                        if finalfound_2by2 == False:
                            final_pieces.append(Piece(True, False, x, line_index, None))
                            finalfound_2by2 = True
                        elif finalfound_2by2 == True:
                            finalfound_2by2 = False
                elif ch == '\n':
                    if skip_one_line == False and one_found == True:
                        skip_one_line = True
                        one_found = False
                    elif skip_one_line == True:
                        skip_one_line = False
        line_index += 1
        
    puzzle_file.close()
    board = Board(height_, pieces)
    goal_board = Board(height_, final_pieces)
    return board, goal_board


def grid_to_string(grid):
    string = ""
    for i, line in enumerate(grid):
        for ch in line:
            string += ch
        string += "\n"
    return string

def if_goal_state(current, goal):
    return current.board == goal

def get_heuristic(current, goal):
    goal_pieces = goal.pieces[:]
    h = float("inf")
    seen = set()    

    for now in current.board.pieces:
        for want in goal_pieces:
            if now.type == want.type:
                if now in seen:
                    distance = abs(now.coord_x - want.coord_x) + abs(now.coord_y - want.coord_y)
                    if (distance < now.h_value):
                        now.h_value = distance
                else:
                    now.h_value = abs(now.coord_x - want.coord_x) + abs(now.coord_y - want.coord_y)
                    seen.add(now)

    return current.board.total_h()

def get_solution(current):
    moves = [current]

    parent = current.parent

    while not parent == None:
        moves.append(parent)
        parent = parent.parent

    return moves


def make_state(p, current, goal, x_change, y_change):

    cp = copy_board(current.board)
    state = State(cp, 0, 0, current.depth + 1, parent=current)
    state.board.pieces[p].set_coords(state.board.pieces[p].coord_x + x_change, state.board.pieces[p].coord_y + y_change)
    state.board.update_board()
    state.hfn = get_heuristic(state, goal)
    state.f = state.hfn + state.depth
    state.board.find_empty_spaces()
    return state

def copy_board(board):
    copyboard = None
    pieces = []

    for piece in board.pieces:
        pieces.append(copy.copy(piece))

    copyboard = Board(board.height, pieces)

    return copyboard



def check_all_directions(current_piece, p, current, goal, x_right, x_left, y_down, y_up):
        moves = []
        if (current_piece.type == "2x2" or current_piece.type == "1x2"):
            if (current_piece.coord_x + x_right, current_piece.coord_y) in current.board.blanks and (current_piece.coord_x + x_right, current_piece.coord_y + 1) in current.board.blanks:
                moves.append(make_state(p, current, goal, 1, 0))
            if (current_piece.coord_x - x_left, current_piece.coord_y) in current.board.blanks and (current_piece.coord_x - x_left, current_piece.coord_y + 1) in current.board.blanks:
                moves.append(make_state(p, current, goal, -1, 0))
        else:
            if (current_piece.coord_x + x_right, current_piece.coord_y) in current.board.blanks:
                moves.append(make_state(p, current, goal, 1, 0))
            if (current_piece.coord_x - x_left, current_piece.coord_y) in current.board.blanks:
                moves.append(make_state(p, current, goal, -1, 0))
        if (current_piece.type == "2x2" or current_piece.type == "2x1"):
            if (current_piece.coord_x, current_piece.coord_y + y_down) in current.board.blanks and (current_piece.coord_x + 1, current_piece.coord_y + y_down) in current.board.blanks:
                moves.append(make_state(p, current, goal, 0, 1))
            if (current_piece.coord_x, current_piece.coord_y - y_up) in current.board.blanks and (current_piece.coord_x + 1, current_piece.coord_y - y_up) in current.board.blanks:
                moves.append(make_state(p, current, goal, 0, -1))
        else:
            if (current_piece.coord_x, current_piece.coord_y + y_down) in current.board.blanks:
                moves.append(make_state(p, current, goal, 0, 1))
            if (current_piece.coord_x, current_piece.coord_y - y_up) in current.board.blanks:
                moves.append(make_state(p, current, goal, 0, -1))

        return moves

def generate_succesor(current, goal):
    successors = []

    for p in range(len(current.board.pieces)):
        current_piece = current.board.pieces[p]
        if current_piece.type == "2x2":
            successors += check_all_directions(current_piece, p, current, goal, 2, 1, 2, 1)
        elif current_piece.type == "1x1":
            successors += check_all_directions(current_piece, p, current, goal, 1, 1, 1, 1)   
        elif current_piece.type == "1x2":
            successors += check_all_directions(current_piece, p, current, goal, 1, 1, 2, 1)
        elif current_piece.type == "2x1":
            successors += check_all_directions(current_piece, p, current, goal, 2, 1, 1, 1)
    return successors

def dfs(board, goal_board):
    frontier = [board]
    explored = set()
    curr = None
    while frontier != []:
        curr = frontier.pop()
        if not curr.board in explored:
            explored.add(curr.board)
            if if_goal_state(curr, goal_board):
                return curr
            frontier.extend(generate_succesor(curr, goal_board))

    return None

def astar(board, goal_board):
    frontier = minHeap()
    frontier.insert(board)
    explored = set()
    curr = None
    while not frontier.is_empty():
        curr = frontier.extract_min()
        if not curr.board in explored:
            explored.add(curr.board)
            if if_goal_state(curr, goal_board):
                return curr
            successors = generate_succesor(curr, goal_board)
            for successor in successors:
                frontier.insert(successor)
    return None



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board, goal_board = read_from_file(args.inputfile)

    board_state = State(board, 0, 0, 0)
    board_state.hfn = get_heuristic(board_state, goal_board)
    board_state.f = board_state.depth + board_state.hfn

    if args.algo == 'dfs':
        dfs = dfs(board_state, goal_board)
        solution_file = open(args.outputfile, 'w')

        if dfs == None:
            solution_file.write("No solution")

        else:
            dfs_solution = get_solution(dfs)

            if (len(dfs_solution) == 1):
                solution_file.write(grid_to_string(dfs_solution[0].board.grid))
                solution_file.write('\n')
                solution_file.write(grid_to_string(dfs_solution[0].board.grid))
                solution_file.write('\n')
            else:

                for state in range(len(dfs_solution) -1, -1, -1):
                    solution_file.write(grid_to_string(dfs_solution[state].board.grid))
                    solution_file.write('\n')
        
        solution_file.close()
    
    if args.algo == 'astar':
        astar = astar(board_state, goal_board)
        solution_file = open(args.outputfile, 'w')

        if astar == None:
            solution_file.write("No solution")

        else:
            astar_solution = get_solution(astar)

            if (len(astar_solution) == 1):
                solution_file.write(grid_to_string(astar_solution[0].board.grid))
                solution_file.write('\n')
                solution_file.write(grid_to_string(astar_solution[0].board.grid))
                solution_file.write('\n')

            else:
                for state in range(len(astar_solution) -1, -1, -1):
                    solution_file.write(grid_to_string(astar_solution[state].board.grid))
                    solution_file.write('\n')
        
        solution_file.close()
    #An example of how to write solutions to the outputfile. (This is not a correct solution, of course).
    #with open(args.outputfile, 'w') as sys.stdout:
    #    board.display()
    #    print("")
    #    goal_board.display()

