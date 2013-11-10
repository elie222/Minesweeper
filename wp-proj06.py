import argparse  # mandatory
import random
from collections import deque



class GameStatus(object):
    """Enum of possible Game statuses."""
    __init__ = None
    NotStarted, InProgress, Win, Lose = range(4)


class RippleTypes(object):
    """Enum of possible ripple types."""
    __init__ = None
    Simple, Recursive, Queue = range(3)


class SizeOutOfBoundException(Exception):
    pass


class ScatterException(Exception):
    pass


class BoardFormatException(Exception):
    pass


class DimensionsMismatchException(Exception):
    pass


class IllegalIndicesException(Exception):
    pass


class IllegalMoveException(Exception):
    pass


class Board(object):
    """Represents a board of minesweeper game and its current progress."""

    def __init__(self, rows, columns):
        """Initializes an empty hidden board.

        The board will be in the specified dimensions, without mines in it,
        and all of its cells are in hidden state.

        Args:
            rows: the number of rows in the board
            columns: the number of columns in the board

        Returns:
            None (alters self)

        Raises:
            SizeOutOfBoundException if one of the arguments is non positive,
            or the board size is smaller than 1x2 (rows first) or larger than
            20x50.

        """
        MIN_ROWS = 1
        MAX_ROWS = 20
        MIN_COLS = 2
        MAX_COLS = 50

        if rows < MIN_ROWS or rows > MAX_ROWS or columns < MIN_COLS or columns > MAX_COLS:
            raise SizeOutOfBoundException

        self.rows = rows
        self.columns = columns

        self.board = []
        for i in range(rows):
            new_row = []
            for j in range(columns):
                new_row.append('0H')
            self.board.append(new_row)

    def put_mines(self, mines):
        """Randomly scatter the requested number of mines on the board.

        At the beggining, all cells on the board are hidden and with no mines
        at any of them. This method scatters the requested number of mines
        throughout the board randomly, only if the board is in the beginning
        state (as described here). A cell can host only one mine.
        This method not only scatters the mines on the board, but also updates
        the cells around it (so they will hold the right digit).

        Args:
            mines: the number of mines to scatter

        Returns:
            None (alters self)

        Raises:
            ScatterException if the number of mines is smaller than 1 or larger
            than (rows*columns - 1), and if the board is not in beginning state
            If an exception is raised, the board should be in the same state
            as before calling this method.

        """
        MIN_MINES = 1
        MAX_MINES = (self.rows * self.columns) - 1

        if mines < MIN_MINES or mines > MAX_MINES:
            raise ScatterException

        # check board is in start state
        for i in range(self.rows):
            for j in range(self.columns):
                if not self.get_value(i,j) == '0' or not self.is_hidden(i,j) == 'H':
                    raise ScatterException

        # place mines randomly
        mines_placed = 0

        while mines_placed < mines:
            i = random.randint(0,self.rows-1)
            j = random.randint(0,self.columns-1)
            if not self.get_value(i,j) == '*':
                self.board[i][j] = '*H'
                mines_placed += 1

        # update digits
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j][0] != '*':
                    mines_touching = 0

                    surrounding_coords = [(i+1,j+1), (i-1,j-1), (i+1,j-1), (i-1,j+1), (i+1,j), (i-1,j), (i,j-1), (i,j+1)]
                    neighbour_coords = [(x,y) for (x,y) in surrounding_coords if x>=0 and y>=0 and x<self.rows and y<self.columns]
                    
                    for x,y in neighbour_coords:
                        if self.board[x][y][0] == '*':
                            mines_touching += 1

                    self.board[i][j] = '%dH'%(mines_touching)

    def load_board(self, lines):
        """Loads a board from a sequence of lines.

        This method is used to load a saved board from a sequence of strings
        (that usually represent lines). Each line represents a row in the table
        in the following format:
            XY XY XY ... XY
        Where X is one of the characters: 0-8, * and Y is one of letters: H, S.
        0-8 = number of adjusting mines (0 is an empty, mine-free cell)
        * = represents a mine in this cell
        H = this cell is hidden
        S = this cell is uncovered (can be seen)

        The lines can have multiple whitespace of any kind before and after the
        lines of cells, but between each XY pair there is exactly one space.
        Empty or whitespace-only lines are possible everywhere, even between
        valid lines, or after/before them. It is safe to assume that the
        values are correct (the number represents the number of mines around
        a given cell) and the number of mines is also legal.
        Also note that the combination of '0S' is legal.

        Note that this method doesn't get the first two rows of the file (the
        dimensions) on purpose - they are handled in __init__.

        Args:
            lines: a sequence (list or tuple) of lines with the above
            restrictions

        Returns:
            None (alters self)

        Raises:
            BoardFormatException if the lines are empty (all of them),
            or there are wrong X/Y values etc.
            DimensionsMismatchException if the number of valid lines is
            different than the Board dimensions, or if the number of cells per
            row is unequal on different lines, or different from the Board
            dimensions.
            In case both exceptions are possible, BoardFormatException is
            raised.
            If an exception is raised, it's OK if the board is in an
            unstable state (partly copied).

        """
        validX = [str(x) for x in range(9) + ['*']]
        validY = ['H', 'S']
        self.board = []

        nRows = 0
        for line in lines:
            l = line.strip()
            if len(l) == 0:
                continue

            row = l.split(' ')

            for cell in row:
                if len(cell) != 2:
                    raise BoardFormatException
                if cell[0] not in validX or cell[1] not in validY:
                    raise BoardFormatException

            if len(row) != self.columns:
                raise DimensionsMismatchException

            self.board.append(row)
            nRows += 1

        if nRows == 0:
            raise BoardFormatException

        if nRows != self.rows:
            raise DimensionsMismatchException

    def save_board(self, filename):
        """Saves a Board object to a text file.

        Saves the current Board (self) to a file in the following format:
            line 1:#rows of board
            line 2:#columns of board
            line 3:board row #1
            line 4:board row #2
            ...
        where #rows and #columns are integers representing the dimensions of
        the Board, and the rest of the lines are the rows of the Board
        formatted as described in load_board().
        You can include whitespace before/after every value (including #rows
        and #columns), and include empty or whitespace-only lines everywhere,
        including at the start/end of the file, and between any two lines.

        Args:
            filename: the file name (as string) to write to, can be absolute
            or relative path, or even illegal.

        Returns:
            None (and doesn't alters self)

        Raises:
            IOError in case of any file/IO related problem (forward exception
            and don't handle it)

        """
        try:
            f = open(filename, 'w')

            output = ''
            output += (str(self.rows) + '\n')
            output += (str(self.columns) + '\n')
            for i in range(self.rows):
                for j in range(self.columns):
                    output += (self.board[i][j] + ' ')
                output += '\n'

            f.write(output)
            f.close()
        except:
            raise IOError

    def get_value(self, row, column):
        """Returns the value of the cell at the given indices.

        The return value is a string of one character, out of 0-8 + '*'.

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            If the cell is empty and has no mines around it, return '0'.
            If it has X mines around it (and none in it), return 'X' (digit
            character between 1-8).
            If it has a mine in it return '*'.

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).

        """
        self.checkIndices(row, column)

        return self.board[row][column][0]

    def is_hidden(self, row, column):
        """Returns if the given cell is in hidden or uncovered state.

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            'H' if the cell is hidden, or 'S' if it's uncovered (can be seen).

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).

        """
        self.checkIndices(row, column)

        if self.board[row][column][1] == 'H':
            return 'H'
        else:
            return 'S'

    def uncover(self, row, column):
        """Changes the status of a cell from hidden to seen.

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            None (alters self)

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).
            IllegalMoveException if the cell was already uncovered before
            (and the indices given are legal).

        """
        self.checkIndices(row, column)

        if self.is_hidden(row, column) == 'S':
            raise IllegalMoveException
        else:
            self.board[row][column] = self.board[row][column][0] + 'S'

    def get_ripple_type(self):
        """Returns the ripple type of the current board.

        Please note that this method should return a constant value, depending
        on your implementation, and not on some board configurations.

        Returns:
            one of RippleType values (Simple, Recursive or Queue).
        """
        return RippleTypes.Queue

    def ripple_sequence(self, row, column):
        """Returns the ripple sequence starting on the specified cell.

        Ripple sequence is the sequence of cells to be unvcovered when the cell
        in the row/column position is uncovered. Rippling, for each of the 3
        methods, starts at the upper line (if not the upper row and still
        uncovered) and then moves in a clockwise direction (again, if not on an
        edge row/column or already uncovered).
        For example (we will denote r,c as abbreviations):
            Simple: [(r-1, c), (r-2, c), ... , (r, c+1), (r, c+2) ...] and
                continues over row r and column c.
            Recursive: [(r-1, c), *ripple_sequence(r-1, c), (r, c+1),
                        *ripple_sequence(r, c+1), ...]
                Note that a cell can't appear in the ripple sequence more than
                once.
            Queue: [(r-1, c), (r-1, c+1), ... , according to BFS queue]
        If some direction has no rippling cells (=the cell is on an edge)
        then it is simply skipped. If the given cell has mines around it or
        there are no cells to ripple, return an empty sequence (e.g. []).

        A cell which is already covered, or has a non-zero value, stops rippling
        in that direction only (simple ripple) or with this cell (queue/recursive).
        You can assume that the cell at (row, column) is already uncovered when
        implementing this method.

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            A sequence of (r,c) tuples (both integers) to ripple, or empty
            sequence in case there's nothing to ripple. Note this doesn't
            alters self, so that consecutive calls to ripple_sequence() with
            the same row and column will return the same sequence.

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).

        """
        self.checkIndices(row, column)

        ripple_seq = []

        queue = deque([(row, column)])

        while len(queue) != 0:
            current_cell = queue.popleft()
            ripple_seq.append(current_cell)
            if self.get_value(current_cell[0],current_cell[1]) != '0':
                continue
            neighbours = self.get_neighbours(current_cell)
            hidden_neighbours = [x for x in neighbours if self.is_hidden(x[0], x[1]) == 'H']
            new_neighbours = [x for x in hidden_neighbours if x not in ripple_seq and x not in queue]
            queue.extend(new_neighbours)

        # ripple_seq[0] should be (row, cell)
        return ripple_seq[1:]

    def get_neighbours(self, cell):
        r = cell[0]
        c = cell[1]

        all_possible_neighbours = [(r-1, c), (r-1, c+1), (r, c+1), (r+1, c+1), 
        (r+1, c), (r+1, c-1), (r, c-1), (r-1, c-1)]

        neighbours = [(x,y) for (x,y) in all_possible_neighbours 
        if x>=0 and x<self.rows and y>=0 and y<self.columns]

        return neighbours

    def __str__(self):
        string = ''

        # 1st row
        string += ''.join(['%-2s'%(x) for x in [''] + range(self.rows)])
        string += '\n'

        for i in range(self.rows):
            string += '%-2s'%(i)
            for j in range(self.columns):
                if self.is_hidden(i,j) == 'H':
                    string += '%-2s'%('H')
                else:
                    string += '%-2s'%(self.get_value(i,j))
            string += '\n'

        return string[:-2]

    def checkIndices(self, row, column):
        if row<0 or row>=self.rows or column<0 or column>=self.columns:
            raise IllegalIndicesException


class Game(object):
    """Handles a game of minesweeper by supplying UI to Board object."""

    def __init__(self, board):
        """Initializes a Game object with the given Board object.

        The Board object can be a board in any given status or stage.

        Args:
            board: a Board object to continue (or start) playing.

        Returns:
            None (alters self)

        Raises:
            Nothing (assume board is legal).

        """
        self.board = board

    def get_status(self):
        """Returns the current status of the game.

        The current status of the game is as followed:
            NotStarted: if all cells are hidden.
            InProgress: if some cells are hidden and some are uncovered, and
            no cell with a mine is uncovered.
            Lose: a cell with mine is uncovered.
            Win: All non-mine cells are uncovered, and all mine cells are
            covered.

        Returns:
            one of GameStatus values (doesn't alters self)

        """
        containsUncoveredCell = False
        containsCoveredNonMineCell = False
        for i in range(self.board.rows):
            for j in range(self.board.columns):
                value = self.board.get_value(i,j)
                hidden = True if self.board.is_hidden(i,j) == 'H' else False
                if not hidden and value == '*':
                    return GameStatus.Lose
                if not hidden:
                    containsUncoveredCell = True
                if value != '*' and hidden:
                    containsCoveredNonMineCell = True

        if not containsUncoveredCell:
            return GameStatus.NotStarted
        elif not containsCoveredNonMineCell:
            return GameStatus.Win
        else:
            return GameStatus.InProgress

    def make_move(self, row, column):
        """Makes a move by uncovering the given cell and unrippling it's area.

        The move flow is as following:
        1. Uncover the cell
        2. If the cell is a mine - return
        3. if the cell is not a mine, ripple (if value = 0) and uncover all
            cells according to the ripple sequence, then return

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            the cell's value.

        Raises:
            IllegalMoveException, IllegalIndicesException (generated by Board)

        """
        self.board.uncover(row, column)
        
        cell_value = self.board.get_value(row, column)
        if cell_value != '0':
            return cell_value

        ripple_seq = self.board.ripple_sequence(row, column)
        for (x,y) in ripple_seq:
            self.board.uncover(x,y)

        return cell_value

    def run(self):
        """Runs the game loop.

        At each turn, prints the following:
            current state of the board
            game status
            available actions
        And then wait for input and act accordingly.
        More details are in the project's description.

        Returns:
            None

        Raises:
            Nothing

        """
        while True:
            # print board
            print self.board

            # print game status
            status = self.get_status()
            status_string = None
            if status == GameStatus.NotStarted:
                status_string = 'NotStarted'
            elif status == GameStatus.InProgress:
                status_string = 'InProgress'
            elif status == GameStatus.Win:
                status_string = 'Win'
            elif status == GameStatus.Lose:
                status_string = 'Lose'

            print 'Game status: %s'%(status_string)

            # print available actions
            if status == GameStatus.NotStarted or status == GameStatus.InProgress:
                print 'Available actions: (1) Save | (2) Exit | (3) Move'
            else:
                print 'Available actions: (1) Save | (2) Exit'

            # user input
            ch = raw_input('Enter selection: ')
            if ch == '1':
                filename = raw_input('Enter filename: ')
                try:
                    self.board.save_board(filename)
                except:
                    print 'Save operation failed'
                print 'Save operation done'
            elif ch == '2':
                print 'Goodbye :)'
                return
            elif ch == '3':
                if status == GameStatus.NotStarted or status == GameStatus.InProgress:
                    move = raw_input('Enter row then column (space separated): ')
                    try:
                        r, c = move.split(' ')
                        self.make_move(int(r), int(c))
                    except:
                        print 'Illegal move values'
                else:
                    print 'Illegal choice'
            else:
                print 'Illegal choice'

def main():
    """Starts the game by parsing the arguments and initializing.

    If an input file argument was given, the file is loaded (even if other
    legal command line argument were given). If any error occurs while parsing
    the input file and creating the board, print "Badly-formatted input file"
    and return (None).

    If input file wasn't given, create a board with the rows/columns/mines
    values given (if legal), and if not print
    "Illegal rows/columns/mines values" and return.
    In case both an input file was given and other parameters, ignore the
    others (if they passes argparse legality check), and use only the input
    file. For example, in case we get "-i sample -r 2 -c a" argparse should
    print an error message, but in case we get "-i sample -r 2 -c 2" just use
    the input file and ignore the rest (even if there are missing parameters).

    All arguments (input file, rows, columns and mines) should be checked by
    argparse and converted to file descriptor (input file) or integers (others)
    by argparse itself, and if an error occurs, like non-existing file or
    non-integer value, argparse should show it's error message without any
    additions. The same goes for illegal options in the command line.

    Returns:
        None

    Raises:
        Nothing

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='name of input file', type=argparse.FileType('r'))
    parser.add_argument('-r', '--rows', help='number of rows', type=int, default=1)
    parser.add_argument('-c', '--columns', help='number of columns', type=int, default=2)
    parser.add_argument('-m', '--mines', help='number of mines', type=int, default=1)
    args = parser.parse_args()

    # load input file
    board = None
    if args.input:
        try:
            rows = None
            columns = None
            for line in args.input:
                l = line.strip()
                if len(l) == 0:
                    continue
                if not rows:
                    rows = int(l)
                    continue
                if not columns:
                    columns = int(l)
                    break
            board = Board(rows, columns)
            board.load_board(list(args.input))
        except:
            print 'Badly-formatted input file'
            return
    else:
        try:
            board = Board(args.rows, args.columns)
            board.put_mines(args.mines)
        except:
            print 'Illegal rows/columns/mines values'
            return

    game = Game(board)
    game.run()

if __name__ == '__main__':
    main()

# ADD NO CODE OUTSIDE MAIN() OR OUTSIDE A FUNCTION/CLASS (NO GLOBALS), EXCEPT
# IMPORTS WHICH ARE FINE
