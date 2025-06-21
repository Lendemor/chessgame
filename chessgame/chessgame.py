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

    grid: rx.Field[list[list[Piece]]] = rx.field(default_grid.copy())

    current_player: rx.Field[PlayerType] = rx.field(PlayerType.WHITE)

    @rx.event
    def reset_grid(self):
        """Resets the grid to the default state."""
        self.grid = default_grid.copy()

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
        # Update the grid with the dropped piece
        # params = rxe.dnd.DropTarget.collected_params
        print(row, col, data)
        return rx.toast(
            f"Piece dropped at {COL_NOTATION[col]}{row + 1}",
        )
        # piece = PieceType[piece_type]
        # player = PlayerType.WHITE if piece_type[0] == "W" else PlayerType.BLACK
        # self.grid[row][col] = (piece, player)


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
        class_name="w-full",
    )

    draggable_piece = rxe.dnd.draggable(
        still_piece,
        type=piece.type.to(str),
        can_drag=ChessState.can_drag_piece(),  # type: ignore
    )

    return rx.cond(
        ncond,
        rx.box(height="100%", width="100%"),  # Empty box with proper dimensions
        draggable_piece,
    )


@rx.memo
def chess_square(row: int, col: int) -> rx.Component:
    """
    Renders a single square of the chessboard.
    The color is determined by the row and column.
    """
    player_id = (row + col) % 2
    params = rxe.dnd.DropTarget.collected_params

    drop_target = rxe.dnd.drop_target(
        rx.box(
            chess_piece(row=row, col=col),
            class_name="w-full aspect-square",
            background_color=rx.cond(player_id == 0, "#E7E5E4", "#44403C"),
            z_index=1,
            min_height="60px",  # Ensure minimum height for visibility
        ),
        can_drop=ChessState.can_drop_piece(),  # type: ignore
        on_drop=ChessState.on_piece_drop(row, col, params),
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
            class_name="gap-0",
        ),
        width="70vh",
        border="1px solid #000",
        # class_name="w-96",
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.vstack(
            rx.heading("Chess Game", class_name="text-3xl"),
            rx.text("Current Player: ", ChessState.current_player),
            rx.container(
                chessboard(),
                size="2",
            ),
        ),
        height="100vh",
    )


app = rxe.App()
app.add_page(index)
