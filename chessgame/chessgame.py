"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from typing import Any, Callable
import reflex as rx
import reflex_enterprise as rxe
from reflex_enterprise.components.dnd import DragSourceMonitor, DropTargetMonitor

from .chess import Piece, PieceType, PlayerType, NO_PIECE
from .chess.board import create_default_board, copy_board
from .chess.engine import ChessEngine


class ChessState(rx.State):
    """The app state."""

    grid: rx.Field[list[list[Piece]]] = rx.field(
        default_factory=lambda: copy_board(create_default_board())
    )

    current_player: rx.Field[PlayerType] = rx.field(
        default_factory=lambda: PlayerType.WHITE
    )

    turn_validation_enabled: rx.Field[bool] = rx.field(default_factory=lambda: True)

    # For move highlighting
    dragging_piece_row: rx.Field[int] = rx.field(default_factory=lambda: -1)
    dragging_piece_col: rx.Field[int] = rx.field(default_factory=lambda: -1)
    
    # Game state
    game_over: rx.Field[bool] = rx.field(default_factory=lambda: False)
    winner: rx.Field[str] = rx.field(default_factory=lambda: "")  # "WHITE", "BLACK", or "DRAW"
    
    # Move history
    move_history: rx.Field[list[str]] = rx.field(default_factory=lambda: [])

    @rx.event
    def reset_grid(self):
        """Resets the grid to the default state."""
        self.grid = copy_board(create_default_board())
        self.current_player = PlayerType.WHITE
        self.game_over = False
        self.winner = ""
        self.move_history = []
        return rx.toast("Game reset! White starts.")

    @rx.event
    def toggle_turn_validation(self):
        """Toggles turn validation on/off for testing."""
        self.turn_validation_enabled = not self.turn_validation_enabled
        status = "enabled" if self.turn_validation_enabled else "disabled"
        return rx.toast(f"Turn validation {status}")

    @rx.event
    def copy_move_history(self):
        """Copies the move history to clipboard."""
        history_text = "\n".join(self.move_history) if self.move_history else "No moves yet"
        return [
            rx.set_clipboard(history_text),
            rx.toast("Move history copied to clipboard!")
        ]

    @rx.event
    def start_drag(self, row: int, col: int):
        """Called when starting to drag a piece."""
        self.dragging_piece_row = row
        self.dragging_piece_col = col
        print(f"Started dragging piece at ({row}, {col})")

    @rx.event
    def end_drag(self):
        """Called when ending drag."""
        print(
            f"Ended dragging piece from ({self.dragging_piece_row}, {self.dragging_piece_col})"
        )
        self.dragging_piece_row = -1
        self.dragging_piece_col = -1

    def is_drag_source(self, row: int, col: int) -> bool:
        """Check if this square is the source of the current drag."""
        return (
            self.dragging_piece_row == row
            and self.dragging_piece_col == col
            and self.dragging_piece_row != -1
        )

    def is_valid_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates if a move is legal according to chess rules."""
        return ChessEngine.is_valid_move(self.grid, from_row, from_col, to_row, to_col)

    def is_in_check(self, player: PlayerType) -> bool:
        """Check if the given player's king is in check."""
        return ChessEngine.is_in_check(self.grid, player)

    def would_leave_king_in_check(
        self, from_row: int, from_col: int, to_row: int, to_col: int, player: PlayerType
    ) -> bool:
        """Check if a move would leave the player's king in check."""
        return ChessEngine.would_leave_king_in_check(
            self.grid, from_row, from_col, to_row, to_col, player
        )

    @rx.var
    def current_player_in_check(self) -> bool:
        """Check if the current player is in check."""
        return self.is_in_check(self.current_player)

    def _get_chess_notation(
        self,
        piece_type: PieceType,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        is_capture: bool,
    ) -> str:
        """Generates proper chess notation for a move."""
        return ChessEngine.get_chess_notation(
            piece_type, from_row, from_col, to_row, to_col, is_capture
        )
    
    def check_game_ending_conditions(self):
        """Check if the game has ended due to checkmate or stalemate."""
        if self.game_over:
            return  # Game already over
        
        # Debug: Check game ending conditions
        is_in_check = ChessEngine.is_in_check(self.grid, self.current_player)
        legal_moves = ChessEngine.get_all_legal_moves(self.grid, self.current_player)
        print(f"Debug - Player: {self.current_player}, In check: {is_in_check}, Legal moves: {len(legal_moves)}")
        if len(legal_moves) <= 5:  # Show legal moves if there are few
            for move in legal_moves:
                from_r, from_c, to_r, to_c = move
                piece = self.grid[from_r][from_c]
                # Test if this move would actually leave king in check
                would_be_in_check = ChessEngine.would_leave_king_in_check(self.grid, from_r, from_c, to_r, to_c, self.current_player)
                from_square = f"{chr(ord('A') + from_c)}{8-from_r}"
                to_square = f"{chr(ord('A') + to_c)}{8-to_r}"
                print(f"  Legal move: {piece.type.value} {from_square} → {to_square} - Would leave in check: {would_be_in_check}")
                
        # Extra debug: Show current board state
        print("Current board state:")
        for r in range(8):
            row_str = ""
            for c in range(8):
                p = self.grid[r][c]
                if p.type.value == "none":
                    row_str += ".. "
                else:
                    row_str += f"{p.owner.value}{p.type.value[0].upper()} "
            print(f"  Row {r}: {row_str}")
            
        # Extra debug: Check what squares the black queen can attack
        queen_pos = None
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p.type.value == "queen" and p.owner.value == "B":
                    queen_pos = (r, c)
                    break
        if queen_pos:
            qr, qc = queen_pos
            queen_square = f"{chr(ord('A') + qc)}{8-qr}"
            print(f"Black queen at {queen_square}")
            # Check which squares around white king the queen can attack
            king_squares = [(6,3), (6,4), (6,5), (7,3), (7,4), (7,5)]  # D2, E2, F2, D1, E1, F1
            for kr, kc in king_squares:
                can_attack = ChessEngine.is_valid_move(self.grid, qr, qc, kr, kc)
                square_name = f"{chr(ord('A') + kc)}{8-kr}"
                print(f"  Queen can attack {square_name}: {can_attack}")
                
            # Also check the full diagonal path from H4 to E1
            print("Diagonal path from H4 to E1:")
            diagonal_squares = [(4,7), (5,6), (6,5), (7,4)]  # H4, G3, F2, E1
            for i, (dr, dc) in enumerate(diagonal_squares):
                piece = self.grid[dr][dc]
                square_name = f"{chr(ord('A') + dc)}{8-dr}"
                piece_desc = f"{piece.owner.value}{piece.type.value[0].upper()}" if piece.type.value != "none" else ".."
                print(f"  {square_name}: {piece_desc}")
        
        # Check current player for checkmate/stalemate
        if ChessEngine.is_checkmate(self.grid, self.current_player):
            self.game_over = True
            self.winner = "BLACK" if self.current_player == PlayerType.WHITE else "WHITE"
            winner_name = "Black" if self.winner == "BLACK" else "White"
            return rx.toast(f"Checkmate! {winner_name} wins!")
        
        elif ChessEngine.is_stalemate(self.grid, self.current_player):
            self.game_over = True
            self.winner = "DRAW"
            return rx.toast("Stalemate! The game is a draw.")
        
        return None

    @classmethod
    def can_drag_piece(cls) -> Callable[[rx.Var[Any], DragSourceMonitor], rx.Var[bool]]:
        @rxe.static
        def _can_drag(item: rx.Var[Any], monitor: DragSourceMonitor) -> rx.Var[bool]:
            return True  # Allow dragging all pieces for now

        return _can_drag

    @classmethod
    def can_drop_piece(cls) -> Callable[[rx.Var[Any], DropTargetMonitor], rx.Var[bool]]:
        @rxe.static
        def _can_drop(item: rx.Var[Any], monitor: DropTargetMonitor) -> rx.Var[bool]:
            return True  # Allow dropping on all squares for now

        return _can_drop

    @rx.event
    def on_piece_drop(
        self,
        row: int,
        col: int,
        data: dict,
    ):
        """Handles the drop event for a chess piece."""
        print(f"Drop event: target=({row}, {col}), data={data}")
        
        # Prevent moves if game is over
        if self.game_over:
            return rx.toast("Game is over! Reset to play again.")

        # Set drag state if not already set (for highlighting)
        if data and "row" in data and "col" in data and self.dragging_piece_row == -1:
            self.start_drag(data["row"], data["col"])

        # Extract the dropped item data
        if data and "row" in data and "col" in data:
            source_row = data.get("row")
            source_col = data.get("col")
            piece_type_str = data.get("piece_type")
            piece_owner_str = data.get("piece_owner")

            # Convert string values back to enums
            piece_type = PieceType(piece_type_str) if piece_type_str else None
            piece_owner = PlayerType(piece_owner_str) if piece_owner_str else None

            # Move the piece
            if (
                source_row is not None
                and source_col is not None
                and piece_type
                and piece_owner
            ):
                # Check if dropping on the same square (cancel move)
                if source_row == row and source_col == col:
                    self.end_drag()
                    return rx.toast("Move cancelled")

                # Check if it's the correct player's turn (if validation enabled)
                if self.turn_validation_enabled and piece_owner != self.current_player:
                    self.end_drag()
                    return rx.toast(f"It's {self.current_player.value}'s turn!")

                # Check if destination square is occupied by own piece
                destination_piece = self.grid[row][col]
                if (
                    destination_piece.type != PieceType.NONE
                    and destination_piece.owner == piece_owner
                ):
                    self.end_drag()
                    return rx.toast("Cannot capture your own piece!")

                # Validate the move according to chess rules
                if not self.is_valid_move(source_row, source_col, row, col):
                    self.end_drag()
                    return rx.toast("Invalid move for this piece!")

                # Check if this move would leave the player's own king in check
                if self.would_leave_king_in_check(
                    source_row, source_col, row, col, piece_owner
                ):
                    self.end_drag()
                    return rx.toast("Cannot leave your king in check!")

                # Create the piece object
                moved_piece = Piece(piece_type, piece_owner)

                # Check if capturing an opponent's piece
                is_capture = (
                    destination_piece.type != PieceType.NONE
                    and destination_piece.owner != piece_owner
                )

                # Update grid: place piece at destination
                self.grid[row][col] = moved_piece

                # Clear source square
                self.grid[source_row][source_col] = NO_PIECE

                # Reset drag tracking
                self.end_drag()

                # Switch turns (if validation enabled)
                if self.turn_validation_enabled:
                    self.current_player = (
                        PlayerType.BLACK
                        if self.current_player == PlayerType.WHITE
                        else PlayerType.WHITE
                    )

                # Check if the move puts the opponent in check
                opponent = (
                    PlayerType.BLACK
                    if piece_owner == PlayerType.WHITE
                    else PlayerType.WHITE
                )
                opponent_in_check = self.is_in_check(opponent)

                # Show appropriate message with chess notation
                move_notation = self._get_chess_notation(
                    piece_type, source_row, source_col, row, col, is_capture
                )

                # Add to move history with detailed info
                move_count = len(self.move_history) + 1
                move_detail = f"{move_count}. {piece_owner.value} {piece_type.value} ({source_row},{source_col})→({row},{col}) [{move_notation}]"
                self.move_history.append(move_detail)

                # Check for game ending conditions after the move
                game_ending_toast = self.check_game_ending_conditions()
                if game_ending_toast:
                    return game_ending_toast

                # Add check notation if opponent is in check
                if opponent_in_check:
                    move_notation += "+"

                if is_capture:
                    check_msg = " - Check!" if opponent_in_check else ""
                    return rx.toast(
                        f"{move_notation} - Captured {destination_piece.owner.value} {destination_piece.type.value}!{check_msg}",
                    )
                else:
                    check_msg = " - Check!" if opponent_in_check else ""
                    return rx.toast(f"{move_notation}{check_msg}")

        return rx.toast("Invalid move attempt")


pixel_piece_folder = "/pieces2/"


def chess_piece(row: int, col: int) -> rx.Component:
    """
    Renders a chess piece based on the piece type.
    The piece type is determined by the state.
    """
    piece = ChessState.grid[row][col]
    ncond = (piece.type == PieceType.NONE) & (piece.owner == PlayerType.NONE)
    still_piece = rx.image(
        src=f"{pixel_piece_folder}{piece.owner}_{piece.type}.png",
        width="40px",
        height="40px",
        object_fit="contain",
    )

    draggable_piece = rxe.dnd.draggable(
        still_piece,
        type=piece.type.to(str),
        item={
            "row": row,
            "col": col,
            "piece_type": piece.type,
            "piece_owner": piece.owner,
        },
        can_drag=ChessState.can_drag_piece(),  # type: ignore
    )

    return rx.cond(
        ncond,
        rx.box(height="40px", width="40px"),  # Empty box with fixed dimensions
        draggable_piece,
    )


@rx.memo
def chess_square(row: int, col: int) -> rx.Component:
    """
    Renders a single square of the chessboard.
    The color is determined by the row and column.
    """
    player_id = (row + col) % 2

    # Check if this is the drag source by comparing coordinates directly
    is_source = (
        (ChessState.dragging_piece_row == row)
        & (ChessState.dragging_piece_col == col)
        & (ChessState.dragging_piece_row != -1)
    )

    # Determine background color
    base_color = rx.cond(player_id == 0, "#E7E5E4", "#44403C")
    source_color = "#FFD700"  # Gold for drag source

    background_color = rx.cond(is_source, source_color, base_color)

    drop_target = rxe.dnd.drop_target(
        rx.box(
            chess_piece(row=row, col=col),
            class_name="w-full aspect-square",
            background_color=background_color,
            z_index=1,
            height="60px",  # Fixed height for consistency
            width="60px",  # Fixed width for consistency
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        can_drop=ChessState.can_drop_piece(),  # type: ignore
        on_drop=lambda data: ChessState.on_piece_drop(row, col, data),
        accept=[
            PieceType.PAWN.value,
            PieceType.KNIGHT.value,
            PieceType.BISHOP.value,
            PieceType.ROOK.value,
            PieceType.QUEEN.value,
            PieceType.KING.value,
        ],
        cursor=rx.cond(
            rxe.dnd.Draggable.collected_params.is_dragging,
            "grabbing",
            "grab",
        ),
    )
    return drop_target


def chessboard() -> rx.Component:
    """
    Renders the chessboard with row/column legends.
    """
    # Column labels (A-H)
    col_labels = []
    for i, col_letter in enumerate("ABCDEFGH"):
        col_labels.append(
            rx.box(
                rx.text(col_letter, font_weight="bold", text_align="center"),
                width="60px",
                height="30px",
                display="flex",
                align_items="center",
                justify_content="center",
            )
        )

    # Create board rows with row labels
    board_rows = []
    for row in range(8):
        # Row label (8, 7, 6, 5, 4, 3, 2, 1)
        row_label = rx.box(
            rx.text(str(8 - row), font_weight="bold", text_align="center"),
            width="30px",
            height="60px",
            display="flex",
            align_items="center",
            justify_content="center",
        )
        
        # Row squares
        row_squares = []
        for col in range(8):
            row_squares.append(chess_square(row=row, col=col))
        
        # Combine row label with squares
        board_rows.append(
            rx.hstack(
                row_label,
                *row_squares,
                spacing="0",
                align_items="center",
            )
        )

    return rx.vstack(
        # Column labels
        rx.hstack(
            rx.box(width="30px", height="30px"),  # Empty corner
            *col_labels,
            spacing="0",
            align_items="center",
        ),
        # Board with row labels
        rx.vstack(
            *board_rows,
            spacing="0",
            border="2px solid #000",
        ),
        spacing="0",
        align_items="start",
    )


def debug_panel() -> rx.Component:
    """Debug panel with game controls and move history."""
    return rx.vstack(
        rx.heading("Game Controls", size="6"),
        
        # Game status
        rx.vstack(
            rx.cond(
                ChessState.game_over,
                rx.vstack(
                    rx.text("GAME OVER", color="red", font_weight="bold", font_size="lg"),
                    rx.cond(
                        ChessState.winner == "DRAW",
                        rx.text("It's a draw!", color="orange", font_weight="bold"),
                        rx.text(f"{ChessState.winner} wins!", color="green", font_weight="bold"),
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.vstack(
                    rx.text("Current Player: ", ChessState.current_player),
                    rx.cond(
                        ChessState.current_player_in_check,
                        rx.text("IN CHECK!", color="red", font_weight="bold"),
                        rx.text(""),
                    ),
                    spacing="1",
                    align="start",
                ),
            ),
            spacing="2",
            align="start",
            padding="4",
            border="1px solid #ccc",
            border_radius="8px",
        ),
        
        # Control buttons
        rx.vstack(
            rx.button(
                "Reset Game",
                on_click=ChessState.reset_grid,
                background_color="red",
                color="white",
                _hover={"background_color": "darkred"},
                width="100%",
            ),
            rx.button(
                rx.cond(
                    ChessState.turn_validation_enabled,
                    "Disable Turn Validation",
                    "Enable Turn Validation",
                ),
                on_click=ChessState.toggle_turn_validation,
                background_color=rx.cond(
                    ChessState.turn_validation_enabled, "orange", "green"
                ),
                color="white",
                _hover={"opacity": "0.8"},
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        
        # Move history
        rx.vstack(
            rx.hstack(
                rx.heading("Move History", size="5"),
                rx.button(
                    "Copy History",
                    on_click=ChessState.copy_move_history,
                    size="2",
                    background_color="blue",
                    color="white",
                    _hover={"background_color": "darkblue"},
                ),
                spacing="2",
                align="center",
                justify="between",
                width="100%",
            ),
            rx.box(
                rx.foreach(
                    ChessState.move_history,
                    lambda move: rx.text(move, font_size="sm", font_family="monospace", color="black"),
                ),
                height="300px",
                overflow_y="auto",
                border="1px solid #ccc",
                border_radius="4px",
                padding="2",
                width="100%",
                background_color="#ffffff",
            ),
            spacing="2",
            width="100%",
        ),
        
        spacing="4",
        align="start",
        width="350px",
        padding="4",
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.vstack(
            rx.heading("Chess Game", class_name="text-3xl", text_align="center"),
            rx.hstack(
                # Left side - Chessboard
                rx.vstack(
                    chessboard(),
                    align="center",
                ),
                # Right side - Debug panel
                debug_panel(),
                spacing="6",
                align="start",
                justify="center",
            ),
            spacing="4",
            align="center",
        ),
        height="100vh",
        padding="4",
    )


app = rxe.App()
app.add_page(index)
