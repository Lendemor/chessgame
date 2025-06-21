"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import dataclasses
from enum import Enum
from typing import Any, Callable
import reflex as rx
import reflex_enterprise as rxe
from reflex_enterprise.components.dnd import DragSourceMonitor, DropTargetMonitor

COL_NOTATION = "ABCDEFGH"


class PieceType(Enum):
    """Enum for piece types."""

    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"
    NONE = "none"


class PlayerType(Enum):
    """Enum for player types."""

    WHITE = "W"
    BLACK = "B"
    NONE = "none"


@dataclasses.dataclass
class Piece:
    """Class for chess pieces."""

    type: PieceType
    owner: PlayerType

    @property
    def __drag_type__(self) -> str:
        """Returns the drag type for the piece."""
        return self.type.value


NO_PIECE = Piece(PieceType.NONE, PlayerType.NONE)

default_grid: list[list[Piece]] = [
    [
        Piece(PieceType.ROOK, PlayerType.WHITE),
        Piece(PieceType.KNIGHT, PlayerType.WHITE),
        Piece(PieceType.BISHOP, PlayerType.WHITE),
        Piece(PieceType.QUEEN, PlayerType.WHITE),
        Piece(PieceType.KING, PlayerType.WHITE),
        Piece(PieceType.BISHOP, PlayerType.WHITE),
        Piece(PieceType.KNIGHT, PlayerType.WHITE),
        Piece(PieceType.ROOK, PlayerType.WHITE),
    ],
    [
        Piece(PieceType.PAWN, PlayerType.WHITE),
        Piece(PieceType.PAWN, PlayerType.WHITE),
        Piece(PieceType.PAWN, PlayerType.WHITE),
        Piece(PieceType.PAWN, PlayerType.WHITE),
        Piece(PieceType.PAWN, PlayerType.WHITE),
        Piece(PieceType.PAWN, PlayerType.WHITE),
        Piece(PieceType.PAWN, PlayerType.WHITE),
        Piece(PieceType.PAWN, PlayerType.WHITE),
    ],
    [NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE],
    [NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE],
    [NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE],
    [NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE, NO_PIECE],
    [
        Piece(PieceType.PAWN, PlayerType.BLACK),
        Piece(PieceType.PAWN, PlayerType.BLACK),
        Piece(PieceType.PAWN, PlayerType.BLACK),
        Piece(PieceType.PAWN, PlayerType.BLACK),
        Piece(PieceType.PAWN, PlayerType.BLACK),
        Piece(PieceType.PAWN, PlayerType.BLACK),
        Piece(PieceType.PAWN, PlayerType.BLACK),
        Piece(PieceType.PAWN, PlayerType.BLACK),
    ],
    [
        Piece(PieceType.ROOK, PlayerType.BLACK),
        Piece(PieceType.KNIGHT, PlayerType.BLACK),
        Piece(PieceType.BISHOP, PlayerType.BLACK),
        Piece(PieceType.QUEEN, PlayerType.BLACK),
        Piece(PieceType.KING, PlayerType.BLACK),
        Piece(PieceType.BISHOP, PlayerType.BLACK),
        Piece(PieceType.KNIGHT, PlayerType.BLACK),
        Piece(PieceType.ROOK, PlayerType.BLACK),
    ],
]


class ChessState(rx.State):
    """The app state."""

    grid: rx.Field[list[list[Piece]]] = rx.field(
        default_factory=lambda: [row.copy() for row in default_grid]
    )

    current_player: rx.Field[PlayerType] = rx.field(
        default_factory=lambda: PlayerType.WHITE
    )

    turn_validation_enabled: rx.Field[bool] = rx.field(default_factory=lambda: True)

    # For move highlighting
    dragging_piece_row: rx.Field[int] = rx.field(default_factory=lambda: -1)
    dragging_piece_col: rx.Field[int] = rx.field(default_factory=lambda: -1)

    @rx.event
    def reset_grid(self):
        """Resets the grid to the default state."""
        self.grid = [row.copy() for row in default_grid]
        self.current_player = PlayerType.WHITE
        return rx.toast("Game reset! White starts.")

    @rx.event
    def toggle_turn_validation(self):
        """Toggles turn validation on/off for testing."""
        self.turn_validation_enabled = not self.turn_validation_enabled
        status = "enabled" if self.turn_validation_enabled else "disabled"
        return rx.toast(f"Turn validation {status}")
    
    @rx.event
    def start_drag(self, row: int, col: int):
        """Called when starting to drag a piece."""
        self.dragging_piece_row = row
        self.dragging_piece_col = col
        print(f"Started dragging piece at ({row}, {col})")
    
    @rx.event
    def end_drag(self):
        """Called when ending drag."""
        print(f"Ended dragging piece from ({self.dragging_piece_row}, {self.dragging_piece_col})")
        self.dragging_piece_row = -1
        self.dragging_piece_col = -1
    
    def is_drag_source(self, row: int, col: int) -> bool:
        """Check if this square is the source of the current drag."""
        return (self.dragging_piece_row == row and 
                self.dragging_piece_col == col and 
                self.dragging_piece_row != -1)
    

    def is_valid_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates if a move is legal according to chess rules."""
        # Bounds check
        if not (0 <= to_row < 8 and 0 <= to_col < 8):
            return False

        piece = self.grid[from_row][from_col]
        if piece.type == PieceType.NONE:
            return False

        # Can't move to same square
        if from_row == to_row and from_col == to_col:
            return False

        # Piece-specific validation
        if piece.type == PieceType.PAWN:
            return self._is_valid_pawn_move(
                from_row, from_col, to_row, to_col, piece.owner
            )
        elif piece.type == PieceType.ROOK:
            return self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.BISHOP:
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.KNIGHT:
            return self._is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.QUEEN:
            return self._is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.KING:
            return self._is_valid_king_move(from_row, from_col, to_row, to_col)

        return False

    def _is_valid_pawn_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int, owner: PlayerType
    ) -> bool:
        """Validates pawn moves."""
        direction = (
            1 if owner == PlayerType.WHITE else -1
        )  # White moves down (positive), Black moves up (negative)
        start_row = 1 if owner == PlayerType.WHITE else 6

        # Forward moves
        if from_col == to_col:
            # One square forward
            if to_row == from_row + direction:
                return self.grid[to_row][to_col].type == PieceType.NONE
            # Two squares forward from starting position
            elif from_row == start_row and to_row == from_row + 2 * direction:
                return (
                    self.grid[to_row][to_col].type == PieceType.NONE
                    and self.grid[from_row + direction][to_col].type == PieceType.NONE
                )

        # Diagonal captures
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target_piece = self.grid[to_row][to_col]
            return target_piece.type != PieceType.NONE and target_piece.owner != owner

        return False

    def _is_valid_rook_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates rook moves (horizontal/vertical)."""
        # Must move in straight line
        if from_row != to_row and from_col != to_col:
            return False

        return self._is_path_clear(from_row, from_col, to_row, to_col)

    def _is_valid_bishop_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates bishop moves (diagonal)."""
        # Must move diagonally
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False

        return self._is_path_clear(from_row, from_col, to_row, to_col)

    def _is_valid_knight_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates knight moves (L-shape)."""
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)

        # L-shape: 2+1 or 1+2
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _is_valid_queen_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates queen moves (combination of rook and bishop)."""
        return self._is_valid_rook_move(
            from_row, from_col, to_row, to_col
        ) or self._is_valid_bishop_move(from_row, from_col, to_row, to_col)

    def _is_valid_king_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates king moves (one square in any direction)."""
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)

        # One square in any direction
        return row_diff <= 1 and col_diff <= 1

    def _is_path_clear(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Checks if path between two squares is clear (excluding endpoints)."""
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)

        current_row = from_row + row_step
        current_col = from_col + col_step

        while current_row != to_row or current_col != to_col:
            if self.grid[current_row][current_col].type != PieceType.NONE:
                return False
            current_row += row_step
            current_col += col_step

        return True

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
        # Piece symbols (empty string for pawns)
        piece_symbols = {
            PieceType.KING: "K",
            PieceType.QUEEN: "Q",
            PieceType.ROOK: "R",
            PieceType.BISHOP: "B",
            PieceType.KNIGHT: "N",
            PieceType.PAWN: "",
        }

        piece_symbol = piece_symbols.get(piece_type, "")
        to_square = f"{COL_NOTATION[to_col]}{8 - to_row}"

        # Basic notation
        if piece_type == PieceType.PAWN:
            if is_capture:
                # Pawn captures: e.g., "exd5"
                return f"{COL_NOTATION[from_col]}x{to_square}"
            else:
                # Pawn moves: e.g., "e4"
                return to_square
        else:
            # Piece moves: e.g., "Nf3", "Bxe5"
            capture_symbol = "x" if is_capture else ""
            return f"{piece_symbol}{capture_symbol}{to_square}"

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

                # Show appropriate message with chess notation
                move_notation = self._get_chess_notation(
                    piece_type, source_row, source_col, row, col, is_capture
                )
                if is_capture:
                    return rx.toast(
                        f"{move_notation} - Captured {destination_piece.owner.value} {destination_piece.type.value}!",
                    )
                else:
                    return rx.toast(move_notation)

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
    is_source = (ChessState.dragging_piece_row == row) & (ChessState.dragging_piece_col == col) & (ChessState.dragging_piece_row != -1)

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
    Renders the chessboard using a grid layout.
    Each square is created using the chess_square function.
    """
    squares = []
    for row in range(8):
        for col in range(8):
            squares.append(chess_square(row=row, col=col))

    return rx.box(
        rx.grid(
            *squares,
            columns="8",
            gap="0",
            grid_template_columns="repeat(8, 60px)",
            grid_template_rows="repeat(8, 60px)",
        ),
        width="480px",  # 8 * 60px
        height="480px",  # 8 * 60px
        border="1px solid #000",
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.vstack(
            rx.heading("Chess Game", class_name="text-3xl"),
            rx.hstack(
                rx.text("Current Player: ", ChessState.current_player),
                rx.button(
                    "Reset Game",
                    on_click=ChessState.reset_grid,
                    background_color="red",
                    color="white",
                    _hover={"background_color": "darkred"},
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
                ),
                spacing="4",
                align="center",
            ),
            rx.container(
                chessboard(),
                size="2",
            ),
        ),
        height="100vh",
    )


app = rxe.App()
app.add_page(index)
