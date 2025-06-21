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
    winner: rx.Field[str] = rx.field(
        default_factory=lambda: ""
    )  # "WHITE", "BLACK", or "DRAW"

    # Castling rights - track if king/rooks have moved
    white_king_moved: rx.Field[bool] = rx.field(default_factory=lambda: False)
    white_kingside_rook_moved: rx.Field[bool] = rx.field(default_factory=lambda: False)
    white_queenside_rook_moved: rx.Field[bool] = rx.field(default_factory=lambda: False)
    black_king_moved: rx.Field[bool] = rx.field(default_factory=lambda: False)
    black_kingside_rook_moved: rx.Field[bool] = rx.field(default_factory=lambda: False)
    black_queenside_rook_moved: rx.Field[bool] = rx.field(default_factory=lambda: False)

    # En passant - track target square for en passant capture
    en_passant_target: rx.Field[tuple[int, int] | None] = rx.field(
        default_factory=lambda: None
    )

    # Move history
    move_history: rx.Field[list[str]] = rx.field(default_factory=lambda: [])

    # Undo functionality - store board states and game states
    board_history: rx.Field[list[list[list[Piece]]]] = rx.field(
        default_factory=lambda: []
    )
    player_history: rx.Field[list[PlayerType]] = rx.field(default_factory=lambda: [])

    @rx.event
    def reset_grid(self):
        """Resets the grid to the default state."""
        self.grid = copy_board(create_default_board())
        self.current_player = PlayerType.WHITE
        self.game_over = False
        self.winner = ""
        self.move_history = []
        # Reset castling rights
        self.white_king_moved = False
        self.white_kingside_rook_moved = False
        self.white_queenside_rook_moved = False
        self.black_king_moved = False
        self.black_kingside_rook_moved = False
        self.black_queenside_rook_moved = False
        # Reset en passant
        self.en_passant_target = None
        # Initialize history with starting position
        self.board_history = [copy_board(self.grid)]
        self.player_history = [PlayerType.WHITE]
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
        history_text = (
            "\n".join(self.move_history) if self.move_history else "No moves yet"
        )
        return [
            rx.set_clipboard(history_text),
            rx.toast("Move history copied to clipboard!"),
        ]

    @rx.event
    def undo_last_move(self):
        """Undo the last move."""
        # Need at least 2 states (starting position + 1 move) to undo
        if len(self.board_history) < 2:
            return rx.toast("No moves to undo!")

        # Can't undo if game is over
        if self.game_over:
            return rx.toast("Cannot undo after game is over!")

        # Remove the last move from history
        self.move_history.pop()

        # Remove current state and restore previous state
        self.board_history.pop()  # Remove current board state
        self.player_history.pop()  # Remove current player state

        # Restore previous board and player
        self.grid = copy_board(self.board_history[-1])
        self.current_player = self.player_history[-1]

        # Reset game over state in case we had a checkmate/stalemate
        self.game_over = False
        self.winner = ""

        return rx.toast("Move undone!")

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
        return ChessEngine.is_valid_move(
            self.grid, from_row, from_col, to_row, to_col, self.en_passant_target
        )

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

    def is_castling_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Check if this is a castling move."""
        return ChessEngine.is_castling_move(
            self.grid, from_row, from_col, to_row, to_col
        )

    def is_valid_castling(
        self, from_row: int, from_col: int, to_row: int, to_col: int, player: PlayerType
    ) -> bool:
        """Check if castling move is valid."""
        if player == PlayerType.WHITE:
            return ChessEngine.is_valid_castling(
                self.grid,
                from_row,
                from_col,
                to_row,
                to_col,
                player,
                self.white_king_moved,
                self.white_kingside_rook_moved,
                self.white_queenside_rook_moved,
            )
        else:
            return ChessEngine.is_valid_castling(
                self.grid,
                from_row,
                from_col,
                to_row,
                to_col,
                player,
                self.black_king_moved,
                self.black_kingside_rook_moved,
                self.black_queenside_rook_moved,
            )

    def is_en_passant_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Check if this is an en passant capture."""
        return ChessEngine.is_en_passant_move(
            self.grid, from_row, from_col, to_row, to_col, self.en_passant_target
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

        # Check current player for checkmate/stalemate
        if ChessEngine.is_checkmate(
            self.grid, self.current_player, self.en_passant_target
        ):
            self.game_over = True
            self.winner = (
                "BLACK" if self.current_player == PlayerType.WHITE else "WHITE"
            )
            winner_name = "Black" if self.winner == "BLACK" else "White"
            return rx.toast(f"Checkmate! {winner_name} wins!")

        elif ChessEngine.is_stalemate(
            self.grid, self.current_player, self.en_passant_target
        ):
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

                # Check for special moves
                is_castling = self.is_castling_move(source_row, source_col, row, col)
                is_en_passant = self.is_en_passant_move(
                    source_row, source_col, row, col
                )

                if is_castling:
                    # Validate castling
                    if not self.is_valid_castling(
                        source_row, source_col, row, col, piece_owner
                    ):
                        self.end_drag()
                        return rx.toast("Invalid castling move!")
                else:
                    # Validate regular move according to chess rules
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
                    not is_castling
                    and destination_piece.type != PieceType.NONE
                    and destination_piece.owner != piece_owner
                ) or is_en_passant

                if is_castling:
                    # Execute castling: move both king and rook
                    is_kingside = col > source_col
                    rook_from_col = 7 if is_kingside else 0
                    rook_to_col = 5 if is_kingside else 3

                    # Move king
                    self.grid[row][col] = moved_piece
                    self.grid[source_row][source_col] = NO_PIECE

                    # Move rook
                    rook_piece = self.grid[source_row][rook_from_col]
                    self.grid[source_row][rook_to_col] = rook_piece
                    self.grid[source_row][rook_from_col] = NO_PIECE
                elif is_en_passant:
                    # Execute en passant: move pawn and remove captured pawn
                    self.grid[row][col] = moved_piece
                    self.grid[source_row][source_col] = NO_PIECE

                    # Remove the captured pawn (on the same row as the moving pawn)
                    captured_pawn_row = source_row
                    self.grid[captured_pawn_row][col] = NO_PIECE
                else:
                    # Regular move: place piece at destination
                    self.grid[row][col] = moved_piece
                    # Clear source square
                    self.grid[source_row][source_col] = NO_PIECE

                # Update castling rights when pieces move
                if piece_type == PieceType.KING:
                    if piece_owner == PlayerType.WHITE:
                        self.white_king_moved = True
                    else:
                        self.black_king_moved = True
                elif piece_type == PieceType.ROOK:
                    if piece_owner == PlayerType.WHITE:
                        if source_col == 0:  # Queenside rook
                            self.white_queenside_rook_moved = True
                        elif source_col == 7:  # Kingside rook
                            self.white_kingside_rook_moved = True
                    else:  # Black
                        if source_col == 0:  # Queenside rook
                            self.black_queenside_rook_moved = True
                        elif source_col == 7:  # Kingside rook
                            self.black_kingside_rook_moved = True

                # Update en passant target
                new_en_passant_target = ChessEngine.get_en_passant_target(
                    source_row, source_col, row, col, piece_type, piece_owner
                )
                self.en_passant_target = new_en_passant_target

                # Reset drag tracking
                self.end_drag()

                # Switch turns (if validation enabled)
                if self.turn_validation_enabled:
                    self.current_player = (
                        PlayerType.BLACK
                        if self.current_player == PlayerType.WHITE
                        else PlayerType.WHITE
                    )

                # Save state for undo functionality (after making the move and switching turns)
                self.board_history.append(copy_board(self.grid))
                self.player_history.append(self.current_player)

                # Check if the move puts the opponent in check
                opponent = (
                    PlayerType.BLACK
                    if piece_owner == PlayerType.WHITE
                    else PlayerType.WHITE
                )
                opponent_in_check = self.is_in_check(opponent)

                # Show appropriate message with chess notation
                if is_castling:
                    is_kingside = col > source_col
                    move_notation = "O-O" if is_kingside else "O-O-O"
                elif is_en_passant:
                    # En passant notation: e.g., "exd6 e.p."
                    from_file = chr(ord("a") + source_col)
                    to_square = f"{chr(ord('a') + col)}{8 - row}"
                    move_notation = f"{from_file}x{to_square} e.p."
                else:
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
        width="55px",
        height="55px",
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
        rx.box(height="55px", width="55px"),  # Empty box with fixed dimensions
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
            height="75px",  # Fixed height for consistency
            width="75px",  # Fixed width for consistency
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
                width="75px",
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
            height="75px",
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
                    rx.text(
                        "GAME OVER", color="red", font_weight="bold", font_size="lg"
                    ),
                    rx.cond(
                        ChessState.winner == "DRAW",
                        rx.text("It's a draw!", color="orange", font_weight="bold"),
                        rx.text(
                            f"{ChessState.winner} wins!",
                            color="green",
                            font_weight="bold",
                        ),
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
                "Undo Last Move",
                on_click=ChessState.undo_last_move,
                background_color="purple",
                color="white",
                _hover={"background_color": "darkpurple"},
                width="100%",
                disabled=rx.cond(
                    (ChessState.move_history.length() == 0) | ChessState.game_over,
                    True,
                    False,
                ),
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
                    lambda move: rx.text(
                        move, font_size="sm", font_family="monospace", color="black"
                    ),
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
