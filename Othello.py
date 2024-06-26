import turtle
import random
from pyswip import Prolog
from tkinter import Tk, Button, Label, Entry, messagebox

SCORE_FILE = "scores.txt"

def read_scores(filename=SCORE_FILE):
    try:
        infile = open(filename, "r")
        data = infile.read()
        infile.close()
        return data
    except FileNotFoundError:
        return ""
    except OSError as e:
        print("Error reading the score file:", e)
        return ""

def write_scores(new_data, filename=SCORE_FILE, mode="a"):
    try:
        with open(filename, mode) as outfile:
            outfile.write(new_data)
    except OSError as e:
        print("Error updating the score file:", e)
        return ""

def update_scores(name, score, filename=SCORE_FILE):
    new_record = name + " " + str(score)
    new_data = new_record + "\n"
    scores_data = read_scores(filename)

    if scores_data:
        try:
            records = scores_data.splitlines()
            high_scorer = records[0].rsplit(" ", 1)
            highest_score = int(high_scorer[1])
            if score > highest_score:
                scores_data = new_data + scores_data
                if write_scores(scores_data, filename, "w") == "":
                    return ""
                else:
                    return new_record
        except (ValueError, IndexError) as e:
            print("Error processing score data:", e)
            return ""
    else:
        print("Error: No data in score file")
        return ""

class Board:
    def __init__(self, n):
        prolog.query(f"set_board_size({n})")
        self.n = n
        self.board = [[0] * n for i in range(n)]
        self.square_size = 50
        self.board_color = "gray"
        self.line_color = "black"
        self.tile_size = 20
        self.tile_colors = ["black", "white"]
        self.move = ()

    def draw_board(self):
        turtle.setup(self.n * self.square_size + self.square_size, 
                    self.n * self.square_size + self.square_size)
        turtle.screensize(self.n * self.square_size, self.n * self.square_size)
        turtle.bgcolor("white")

        othello = turtle.Turtle(visible=False)
        othello.penup()
        othello.speed(0)
        othello.hideturtle()

        othello.color(self.line_color, self.board_color)
        
        corner = -self.n * self.square_size / 2
        othello.setposition(corner, corner)
        
        othello.begin_fill()
        for i in range(4):
            othello.pendown()
            othello.forward(self.square_size * self.n)
            othello.left(90)
        othello.end_fill()
        
        for i in range(self.n + 1):
            othello.setposition(corner, self.square_size * i + corner)
            self.draw_lines(othello)
        
        othello.left(90)
        for i in range(self.n + 1):
            othello.setposition(self.square_size * i + corner, corner)
            self.draw_lines(othello)

    def draw_lines(self, turt):
        turt.pendown()
        turt.forward(self.square_size * self.n)
        turt.penup()

    def is_on_board(self, x, y):
        bound = self.n / 2 * self.square_size
        
        if -bound < x < bound and -bound < y < bound:
            return True
        return False

    def is_on_line(self, x, y):
        if self.is_on_board(x, y):   
            if x % self.square_size == 0 or y % self.square_size == 0:
                return True
        return False

    def convert_coord(self, x, y):
        if self.is_on_board(x, y):
            row = int(self.n / 2 - 1 - y // self.square_size)
            col = int(self.n / 2 + x // self.square_size)
            return (row, col)
        return ()

    def get_coord(self, x, y):
        if self.is_on_board(x, y) and not self.is_on_line(x, y):
            self.move = self.convert_coord(x, y)
        else:
            self.move = ()

    def get_tile_start_pos(self, square):
        if square == ():
            return ()
        
        for i in range(2):
            if square[i] not in range(self.n):
                return ()

        row, col = square[0], square[1]

        y = ((self.n - 1) / 2 - row) * self.square_size
        if col < self.n / 2:
            x = (col - (self.n - 1) / 2) * self.square_size - self.tile_size
            r = -self.tile_size
        else:
            x = (col - (self.n - 1) / 2) * self.square_size + self.tile_size
            r = self.tile_size
        prolog.query(f"update_cell({row+1},{col+1},1)")
        return ((x, y), r)

    def draw_tile(self, square, color):
        pos = self.get_tile_start_pos(square)
        if pos:
            coord = pos[0]
            r = pos[1]
        else:
            print("Error drawing the tile...")
            return
        
        tile = turtle.Turtle(visible=False)
        tile.penup()
        tile.speed(0)
        tile.hideturtle()

        tile.color(self.tile_colors[color])

        tile.setposition(coord)
        tile.setheading(90)
        
        tile.begin_fill()
        tile.pendown()
        tile.circle(r)
        tile.end_fill()

    def __str__(self):
        explanation = "State of the board:\n"
        board_str = ""
        for row in self.board:
            board_str += str(row) + "\n" 
        printable_str = explanation + board_str

        return printable_str

    def __eq__(self, other):
        return self.board == other.board

class Othello(Board):

    def __init__(self, n=8):
        self.current_player = 0
        self.num_tiles = [2, 2]
        self.pass_turn_button = None  # Botón para pasar el turno
        Board.__init__(self, n)

    def initialize_board(self):
        if self.n < 2:
            return

        coord1 = int(self.n / 2 - 1)
        coord2 = int(self.n / 2)
        initial_squares = [(coord1, coord2), (coord1, coord1),
                           (coord2, coord1), (coord2, coord2)]
        
        for i in range(len(initial_squares)):
            color = i % 2
            row = initial_squares[i][0]
            col = initial_squares[i][1]
            self.board[row][col] = color + 1
            self.draw_tile(initial_squares[i], color)
    
    def make_move(self):
        if self.is_legal_move(self.move):
            prolog.query(f"update_cell({self.move[0]+1},{self.move[1]+1},{self.current_player + 1})")
            self.board[self.move[0]][self.move[1]] = self.current_player + 1
            self.num_tiles[self.current_player] += 1
            self.draw_tile(self.move, self.current_player)
            self.flip_tiles()
    
    def flip_tiles(self):
        curr_tile = self.current_player + 1 
        for direction in MOVE_DIRS:
            if self.has_tile_to_flip(self.move, direction):
                i = 1
                while True:
                    row = self.move[0] + direction[0] * i
                    col = self.move[1] + direction[1] * i
                    if self.board[row][col] == curr_tile:
                        break
                    else:
                        prolog.query(f"update_cell({row+1},{col+1},1)")
                        self.board[row][col] = curr_tile
                        self.num_tiles[self.current_player] += 1
                        self.num_tiles[(self.current_player + 1) % 2] -= 1
                        self.draw_tile((row, col), self.current_player)
                        i += 1

    def has_tile_to_flip(self, move, direction):
        i = 1
        if self.current_player in (0, 1) and \
           self.is_valid_coord(move[0], move[1]):
            curr_tile = self.current_player + 1
            while True:
                row = move[0] + direction[0] * i
                col = move[1] + direction[1] * i
                if not self.is_valid_coord(row, col) or \
                    self.board[row][col] == 0:
                    return False
                elif self.board[row][col] == curr_tile:
                    break
                else:
                    i += 1
        return i > 1

    def has_legal_move(self):
        for row in range(self.n):
            for col in range(self.n):
                move = (row, col)
                if self.is_legal_move(move):
                    return True
        return False
    
    def get_legal_moves(self):
        moves = []
        for row in range(self.n):
            for col in range(self.n):
                move = (row, col)
                if self.is_legal_move(move):
                    moves.append(move)
        return moves

    def is_legal_move(self, move):
        if move != () and self.is_valid_coord(move[0], move[1]) \
           and self.board[move[0]][move[1]] == 0:
            for direction in MOVE_DIRS:
                if self.has_tile_to_flip(move, direction):
                    return True
        return False

    def is_valid_coord(self, row, col):
        if 0 <= row < self.n and 0 <= col < self.n:
            return True
        return False

    def run(self):
        if self.current_player not in (0, 1):
            print("Error: unknown player. Quit...")
            return
        
        self.current_player = 0
        print("Your turn.")
        self.enable_player_click()  # Activar el evento del jugador humano
        self.enable_pass_turn_button()  # Habilitar el botón para pasar el turno
        turtle.mainloop()

    def enable_pass_turn_button(self):
        self.pass_turn_button = Button(text="Pass Turn", command=self.pass_turn)
        self.pass_turn_button.pack()

    def pass_turn(self):
        print("Player passed turn.")
        self.computer_move()  # Llamar al método para que la computadora juegue

    def enable_player_click(self):
        turtle.onscreenclick(self.play)

    def disable_player_click(self):
        turtle.onscreenclick(None)

    def play(self, x, y):

        self.disable_player_click()  # Desactivar el evento del jugador humano

        if self.has_legal_move():
            self.get_coord(x, y)
            if self.is_legal_move(self.move):
                self.make_move()
                turtle.onscreenclick(None)
                self.computer_move()  # Después del movimiento del jugador, la computadora juega automáticamente

        self.enable_player_click()  # Activar el evento del jugador humano nuevamente

        while True:
            self.current_player = 1
            if self.has_legal_move():
                print("Computer\"s turn.")
                get_possible_moves_from_prolog()
                self.current_player = 0
                if self.has_legal_move():  
                    break
            else:
                break

        
        self.current_player = 0

        if not self.has_legal_move() or sum(self.num_tiles) == self.n ** 2:
            turtle.onscreenclick(None)
            print("-----------")
            self.report_result()
            name = input("Enter your name for posterity\n")
            if not update_scores(name, self.num_tiles[0]):
                print("Your score has not been saved.")
            print("Thanks for playing Othello!")
            close = input("Close the game screen? Y/N\n")
            if close == "Y":
                turtle.bye()
            elif close != "N":
                print("Quit in 3s...")
                turtle.ontimer(turtle.bye, 3000)
        else:
            print("Your turn.")
            turtle.onscreenclick(self.play)

    def computer_move(self):
        self.current_player = 1  # Establecer el turno como el de la computadora
        print("Computer's turn.")
        if self.has_legal_move():  # Verificar si hay movimientos legales disponibles
            moves = self.get_legal_moves()  # Obtener los movimientos legales disponibles
            if moves:
                self.move = random.choice(moves)  # Elegir un movimiento al azar
                self.make_move()  # Realizar el movimiento
                self.current_player = 0  # Restaurar el turno al jugador humano
                print("Your turn.")  # Indicar que es el turno del jugador humano


    def make_random_move(self):
        moves = self.get_legal_moves()
        if moves:
            self.move = random.choice(moves)
            self.make_move()

    def report_result(self):
        print("GAME OVER!!")
        if self.num_tiles[0] > self.num_tiles[1]:
            print("YOU WIN!!",
                  "You have %d tiles, but the computer only has %d!" 
                  % (self.num_tiles[0], self.num_tiles[1]))
        elif self.num_tiles[0] < self.num_tiles[1]:
            print("YOU LOSE...",
                  "The computer has %d tiles, but you only have %d :(" 
                  % (self.num_tiles[1], self.num_tiles[0]))
        else:
            print("IT'S A TIE!! There are %d of each!" % self.num_tiles[0])
    
    def __str__(self):
        player_str = "Current player: " + str(self.current_player + 1) + "\n"
        num_tiles_str = "# of black tiles -- 1: " + str(self.num_tiles[0]) + \
                        "\n" + "# of white tiles -- 2: " + \
                        str(self.num_tiles[1]) + "\n"
        board_str = Board.__str__(self)
        printable_str = player_str + num_tiles_str + board_str

        return printable_str

    def __eq__(self, other):
        return Board.__eq__(self, other) and self.current_player == \
        other.current_player and self.num_tiles == other.num_tiles

def draw_possible_moves(possible_moves):
    turtle.color("red")  # Establecer el color del lápiz en rojo
    for move in possible_moves:
        draw_dot(move)

def draw_dot(position):
    turtle.penup()
    turtle.goto(position)
    turtle.dot(5)  # Dibujar un punto rojo de tamaño 5 en la posición del movimiento
    turtle.pendown()


SQUARE = 50
TILE = 20
BOARD_COLOR = "gray"
LINE_COLOR = "black"
TILE_COLORS = ["black", "white"]
MOVE_DIRS = [(-1, -1), (-1, 0), (-1, +1),
             (0, -1),           (0, +1),
             (+1, -1), (+1, 0), (+1, +1)]

def get_possible_moves_from_prolog():
    possible_moves = []
    try:
        # Ejecuta la consulta en Prolog para obtener los movimientos posibles
        for move in prolog.query("get_possible_moves(Board, PossibleMoves)"):
            possible_moves.append((move["Row"], move["Col"]))
    except Exception as e:
        print("Error ejecutando la consulta Prolog:", e)
    return possible_moves

def start_game():
    global game
    board_size = entry.get()
    if board_size.isdigit():
        size = int(board_size)
        if size in [4, 6, 8, 10]:
            game = Othello(size)
            game.draw_board()
            game.initialize_board()
            game.run()
        else:
            messagebox.showerror("Error", "Please enter a valid board size (4, 6, 8, 10)")
    else:
        messagebox.showerror("Error", "Please enter a valid integer for board size")

def main():
    global entry
    root = Tk()
    root.title("Othello Setup")
    Label(root, text="Enter board size (4, 6, 8, 10):").pack()
    entry = Entry(root)
    entry.pack()
    Button(root, text="Start Game", command=start_game).pack()
    root.mainloop()

if __name__ == "__main__":
    prolog = Prolog()
    prolog.consult("prolog.pl")
    main()