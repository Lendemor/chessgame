"""Chess piece definitions and data models."""

import dataclasses
from enum import Enum


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


# Constant for empty squares
NO_PIECE = Piece(PieceType.NONE, PlayerType.NONE)
