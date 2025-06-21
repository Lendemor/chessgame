"""Chess board state and operations."""

from .pieces import Piece, PieceType, PlayerType, NO_PIECE


def create_default_board() -> list[list[Piece]]:
    """Creates the default chess starting position."""
    return [
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
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
        ],
        [
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
        ],
        [
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
        ],
        [
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
            NO_PIECE,
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
    ]


def find_king(grid: list[list[Piece]], player: PlayerType) -> tuple[int, int] | None:
    """Find the position of the king for the given player."""
    for row in range(8):
        for col in range(8):
            piece = grid[row][col]
            if piece.type == PieceType.KING and piece.owner == player:
                return (row, col)
    return None


def copy_board(grid: list[list[Piece]]) -> list[list[Piece]]:
    """Create a deep copy of the board."""
    return [row.copy() for row in grid]
