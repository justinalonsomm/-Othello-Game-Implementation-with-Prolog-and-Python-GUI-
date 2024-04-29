% Definición de las reglas del juego de Othello en Prolog
:- dynamic get_possible_moves/2.

% Predicado para actualizar los movimientos posibles
update_possible_moves(Board, NewPossibleMoves) :-
    retract(get_possible_moves(Board, _)),
    assertz(get_possible_moves(Board, NewPossibleMoves)).

% Predicado para inicializar el tamaño del tablero
set_board_size(Size) :-
    integer(Size), Size > 0,
    retractall(board_size(_)),
    assertz(board_size(Size)).

% Predicado para obtener el tamaño del tablero
get_board_size(Size) :-
    board_size(Size).

% Predicado para inicializar el tablero
initialize_board(Board) :-
    get_board_size(Size),
    length(Board, Size),
    maplist(initialize_row(Size), Board).

% Predicado para inicializar una fila del tablero
initialize_row(Size, Row) :-
    length(Row, Size),
    maplist(=(0), Row).

% Predicado para obtener el valor de una celda en el tablero
cell_value(Board, Row, Col, Value) :-
    nth0(Row, Board, RowList),
    nth0(Col, RowList, Value).

% Predicado para actualizar el valor de una celda en el tablero
update_cell(Row, Col, Value) :-
    retract(board_size(Board)),
    nth0(Row, Board, RowList),
    replace(RowList, Col, Value, NewRow),
    replace(Board, Row, NewRow, NewBoard),
    assertz(board_size(NewBoard)).

% Predicado para reemplazar un elemento en una lista
replace([_|T], 0, X, [X|T]).
replace([H|T], I, X, [H|R]) :-
    I > 0,
    I1 is I - 1,
    replace(T, I1, X, R).


% Predicado para obtener los movimientos posibles para un jugador en el tablero actual
get_possible_moves(Player,Board, PossibleMoves) :-
    findall([Row, Col], valid_move(Board, Player, Row, Col), PossibleMoves).

% Predicado para validar un movimiento en el tablero
valid_move(Board, Player, Row, Col) :-
    cell_value(Board, Row, Col, 0),
    opposite_player(Player, Opponent),
    between(1, 8, Direction),
    move_direction(Direction, DeltaRow, DeltaCol),
    NewRow is Row + DeltaRow,
    NewCol is Col + DeltaCol,
    inside_board(NewRow, NewCol),
    cell_value(Board, NewRow, NewCol, Opponent),
    is_valid_direction(Board, Player, NewRow, NewCol, DeltaRow, DeltaCol),
    inside_board(Row, Col),
    cell_value(Board, Row, Col, 0).

% Predicado para validar una dirección en el tablero
is_valid_direction(Board, Player, Row, Col, DeltaRow, DeltaCol) :-
    NewRow is Row + DeltaRow,
    NewCol is Col + DeltaCol,
    inside_board(NewRow, NewCol),
    cell_value(Board, NewRow, NewCol, Opponent),
    Opponent \= 0,
    Opponent \= Player,
    next_cell_value(Board, NewRow, NewCol, DeltaRow, DeltaCol, NextCell),
    NextCell = Player.

% Predicado para obtener el valor de la próxima celda en una dirección en el tablero
next_cell_value(Board, Row, Col, DeltaRow, DeltaCol, NextCell) :-
    NextRow is Row + DeltaRow,
    NextCol is Col + DeltaCol,
    cell_value(Board, NextRow, NextCol, NextCell).

% Predicado para verificar si una celda está dentro del tablero
inside_board(Row, Col) :-
    get_board_size(Size),
    between(0, Size, Row),
    between(0, Size, Col).

% Predicado para definir las direcciones de movimiento
move_direction(1, -1, -1).
move_direction(2, -1, 0).
move_direction(3, -1, 1).
move_direction(4, 0, -1).
move_direction(5, 0, 1).
move_direction(6, 1, -1).
move_direction(7, 1, 0).
move_direction(8, 1, 1).

% Predicado para obtener el jugador opuesto
opposite_player(1, 2).
opposite_player(2, 1).