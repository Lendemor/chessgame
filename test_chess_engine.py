"""Unit tests for the chess engine."""

import pytest
from chessgame.chess.pieces import Piece, PieceType, PlayerType, NO_PIECE
from chessgame.chess.board import create_default_board
from chessgame.chess.engine import ChessEngine


class TestBasicMoves:
    """Test basic piece movements."""

    def test_pawn_moves(self):
        """Test pawn movement rules."""
        board = create_default_board()

        # White pawn forward one square
        assert ChessEngine.is_valid_move(board, 6, 4, 5, 4)  # e2-e3

        # White pawn forward two squares from starting position
        assert ChessEngine.is_valid_move(board, 6, 4, 4, 4)  # e2-e4

        # White pawn can't move three squares
        assert not ChessEngine.is_valid_move(board, 6, 4, 3, 4)

        # White pawn can't move backward
        assert not ChessEngine.is_valid_move(board, 6, 4, 7, 4)

        # Black pawn forward one square
        assert ChessEngine.is_valid_move(board, 1, 4, 2, 4)  # e7-e6

        # Black pawn forward two squares from starting position
        assert ChessEngine.is_valid_move(board, 1, 4, 3, 4)  # e7-e5

    def test_pawn_capture(self):
        """Test pawn capture rules."""
        board = create_default_board()

        # Place enemy piece for capture test
        board[5][5] = Piece(PieceType.PAWN, PlayerType.BLACK)

        # White pawn can capture diagonally
        assert ChessEngine.is_valid_move(board, 6, 4, 5, 5)  # e2xf3

        # White pawn can't capture forward
        board[5][4] = Piece(PieceType.PAWN, PlayerType.BLACK)
        assert not ChessEngine.is_valid_move(board, 6, 4, 5, 4)  # blocked

    def test_rook_moves(self):
        """Test rook movement rules."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[4][4] = Piece(PieceType.ROOK, PlayerType.WHITE)  # Rook on e4

        # Horizontal moves
        assert ChessEngine.is_valid_move(board, 4, 4, 4, 7)  # e4-h4
        assert ChessEngine.is_valid_move(board, 4, 4, 4, 0)  # e4-a4

        # Vertical moves
        assert ChessEngine.is_valid_move(board, 4, 4, 0, 4)  # e4-e8
        assert ChessEngine.is_valid_move(board, 4, 4, 7, 4)  # e4-e1

        # Diagonal moves (invalid for rook)
        assert not ChessEngine.is_valid_move(board, 4, 4, 5, 5)
        assert not ChessEngine.is_valid_move(board, 4, 4, 3, 3)

    def test_bishop_moves(self):
        """Test bishop movement rules."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[4][4] = Piece(PieceType.BISHOP, PlayerType.WHITE)  # Bishop on e4

        # Diagonal moves
        assert ChessEngine.is_valid_move(board, 4, 4, 6, 6)  # e4-g2
        assert ChessEngine.is_valid_move(board, 4, 4, 2, 2)  # e4-c6
        assert ChessEngine.is_valid_move(board, 4, 4, 1, 7)  # e4-h7
        assert ChessEngine.is_valid_move(board, 4, 4, 7, 1)  # e4-b1

        # Horizontal/vertical moves (invalid for bishop)
        assert not ChessEngine.is_valid_move(board, 4, 4, 4, 7)
        assert not ChessEngine.is_valid_move(board, 4, 4, 7, 4)

    def test_knight_moves(self):
        """Test knight movement rules."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[4][4] = Piece(PieceType.KNIGHT, PlayerType.WHITE)  # Knight on e4

        # Valid L-shaped moves
        knight_moves = [
            (4, 4, 6, 5),
            (4, 4, 6, 3),  # Down 2, left/right 1
            (4, 4, 2, 5),
            (4, 4, 2, 3),  # Up 2, left/right 1
            (4, 4, 5, 6),
            (4, 4, 3, 6),  # Right 2, up/down 1
            (4, 4, 5, 2),
            (4, 4, 3, 2),  # Left 2, up/down 1
        ]

        for from_r, from_c, to_r, to_c in knight_moves:
            assert ChessEngine.is_valid_move(board, from_r, from_c, to_r, to_c)

        # Invalid moves
        assert not ChessEngine.is_valid_move(board, 4, 4, 4, 5)  # One square
        assert not ChessEngine.is_valid_move(board, 4, 4, 6, 6)  # Diagonal

    def test_queen_moves(self):
        """Test queen movement rules (combination of rook and bishop)."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[4][4] = Piece(PieceType.QUEEN, PlayerType.WHITE)  # Queen on e4

        # Horizontal/vertical (rook-like)
        assert ChessEngine.is_valid_move(board, 4, 4, 4, 7)
        assert ChessEngine.is_valid_move(board, 4, 4, 7, 4)

        # Diagonal (bishop-like)
        assert ChessEngine.is_valid_move(board, 4, 4, 6, 6)
        assert ChessEngine.is_valid_move(board, 4, 4, 2, 2)

        # Invalid knight-like move
        assert not ChessEngine.is_valid_move(board, 4, 4, 6, 5)

    def test_king_moves(self):
        """Test king movement rules."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[4][4] = Piece(PieceType.KING, PlayerType.WHITE)  # King on e4

        # Valid one-square moves in all directions
        king_moves = [
            (4, 4, 5, 4),
            (4, 4, 3, 4),  # Up/down
            (4, 4, 4, 5),
            (4, 4, 4, 3),  # Left/right
            (4, 4, 5, 5),
            (4, 4, 3, 3),  # Diagonals
            (4, 4, 5, 3),
            (4, 4, 3, 5),  # Other diagonals
        ]

        for from_r, from_c, to_r, to_c in king_moves:
            assert ChessEngine.is_valid_move(board, from_r, from_c, to_r, to_c)

        # Invalid multi-square move (but not on back rank to avoid castling detection)
        assert (
            not ChessEngine.is_valid_move(board, 4, 4, 6, 4)
        )  # 2 squares vertical
        assert (
            not ChessEngine.is_valid_move(board, 4, 4, 2, 4)
        )  # 2 squares vertical


class TestPathBlocking:
    """Test that pieces can't jump over other pieces."""

    def test_rook_blocked_path(self):
        """Test rook can't move through pieces."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[4][4] = Piece(PieceType.ROOK, PlayerType.WHITE)  # Rook on e4
        board[4][6] = Piece(PieceType.PAWN, PlayerType.BLACK)  # Blocking pawn on g4

        # Can't move past the blocking piece
        assert not ChessEngine.is_valid_move(board, 4, 4, 4, 7)  # e4-h4 blocked

        # Can move to the blocking piece (capture)
        assert ChessEngine.is_valid_move(board, 4, 4, 4, 6)  # e4xg4

    def test_bishop_blocked_path(self):
        """Test bishop can't move through pieces."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[4][4] = Piece(PieceType.BISHOP, PlayerType.WHITE)  # Bishop on e4
        board[5][5] = Piece(PieceType.PAWN, PlayerType.BLACK)  # Blocking pawn on f3

        # Can't move past the blocking piece
        assert not ChessEngine.is_valid_move(board, 4, 4, 6, 6)  # e4-g2 blocked


class TestOwnPieceBlocking:
    """Test that pieces can't capture their own pieces."""

    def test_cannot_capture_own_piece(self):
        """Test pieces can't move to squares occupied by own pieces."""
        board = create_default_board()

        # White rook can't move to square occupied by white pawn
        assert not ChessEngine.is_valid_move(board, 7, 0, 6, 0)  # Ra1-a2


class TestCheckDetection:
    """Test check detection logic."""

    def test_simple_check(self):
        """Test basic check detection."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)  # White king on e1
        board[0][4] = Piece(PieceType.ROOK, PlayerType.BLACK)  # Black rook on e8

        # White king should be in check
        assert ChessEngine.is_in_check(board, PlayerType.WHITE)
        assert not ChessEngine.is_in_check(board, PlayerType.BLACK)

    def test_no_check(self):
        """Test when king is not in check."""
        board = create_default_board()

        # Starting position has no checks
        assert not ChessEngine.is_in_check(board, PlayerType.WHITE)
        assert not ChessEngine.is_in_check(board, PlayerType.BLACK)


class TestCastling:
    """Test castling rules."""

    def test_castling_detection(self):
        """Test castling move detection."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)  # King on e1

        # King moving 2 squares should be detected as castling
        assert ChessEngine.is_castling_move(board, 7, 4, 7, 6)  # Kingside
        assert ChessEngine.is_castling_move(board, 7, 4, 7, 2)  # Queenside

        # Regular king moves should not be castling
        assert not ChessEngine.is_castling_move(board, 7, 4, 7, 5)  # One square
        assert not ChessEngine.is_castling_move(board, 7, 4, 6, 4)  # Forward

    def test_valid_castling_conditions(self):
        """Test valid castling conditions."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)  # King on e1
        board[7][7] = Piece(PieceType.ROOK, PlayerType.WHITE)  # Rook on h1
        board[7][0] = Piece(PieceType.ROOK, PlayerType.WHITE)  # Rook on a1

        # Valid castling (clear path, pieces haven't moved, not in check)
        assert (
            ChessEngine.is_valid_castling(
                board,
                7,
                4,
                7,
                6,
                PlayerType.WHITE,
                king_moved=False,
                kingside_rook_moved=False,
                queenside_rook_moved=False,
            )
        )

        assert (
            ChessEngine.is_valid_castling(
                board,
                7,
                4,
                7,
                2,
                PlayerType.WHITE,
                king_moved=False,
                kingside_rook_moved=False,
                queenside_rook_moved=False,
            )
        )

    def test_invalid_castling_king_moved(self):
        """Test castling invalid when king has moved."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)
        board[7][7] = Piece(PieceType.ROOK, PlayerType.WHITE)

        # Invalid because king has moved
        assert (
            not ChessEngine.is_valid_castling(
                board,
                7,
                4,
                7,
                6,
                PlayerType.WHITE,
                king_moved=True,
                kingside_rook_moved=False,
                queenside_rook_moved=False,
            )
        )

    def test_invalid_castling_rook_moved(self):
        """Test castling invalid when rook has moved."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)
        board[7][7] = Piece(PieceType.ROOK, PlayerType.WHITE)

        # Invalid because kingside rook has moved
        assert (
            not ChessEngine.is_valid_castling(
                board,
                7,
                4,
                7,
                6,
                PlayerType.WHITE,
                king_moved=False,
                kingside_rook_moved=True,
                queenside_rook_moved=False,
            )
        )

    def test_invalid_castling_blocked_path(self):
        """Test castling invalid when path is blocked."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)
        board[7][7] = Piece(PieceType.ROOK, PlayerType.WHITE)
        board[7][5] = Piece(PieceType.BISHOP, PlayerType.WHITE)  # Blocking piece

        # Invalid because path is blocked
        assert (
            not ChessEngine.is_valid_castling(
                board,
                7,
                4,
                7,
                6,
                PlayerType.WHITE,
                king_moved=False,
                kingside_rook_moved=False,
                queenside_rook_moved=False,
            )
        )


class TestCheckmate:
    """Test checkmate detection."""

    def test_fools_mate(self):
        """Test fool's mate detection."""
        # Set up fool's mate position
        board = create_default_board()

        # 1. f3 e5 2. g4 Qh4#
        board[5][5] = Piece(PieceType.PAWN, PlayerType.WHITE)  # f3
        board[6][5] = NO_PIECE

        board[3][4] = Piece(PieceType.PAWN, PlayerType.BLACK)  # e5
        board[1][4] = NO_PIECE

        board[4][6] = Piece(PieceType.PAWN, PlayerType.WHITE)  # g4
        board[6][6] = NO_PIECE

        board[4][7] = Piece(PieceType.QUEEN, PlayerType.BLACK)  # Qh4
        board[0][3] = NO_PIECE

        # White should be in checkmate
        assert ChessEngine.is_checkmate(board, PlayerType.WHITE)
        assert not ChessEngine.is_checkmate(board, PlayerType.BLACK)

    def test_not_checkmate_with_escape(self):
        """Test position that's check but not checkmate."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)  # White king on e1
        board[0][4] = Piece(PieceType.ROOK, PlayerType.BLACK)  # Black rook on e8

        # King is in check but can move to escape
        assert ChessEngine.is_in_check(board, PlayerType.WHITE)
        assert not ChessEngine.is_checkmate(board, PlayerType.WHITE)


class TestChessNotation:
    """Test chess notation generation."""

    def test_pawn_notation(self):
        """Test pawn move notation."""
        # Regular pawn move
        notation = ChessEngine.get_chess_notation(
            PieceType.PAWN,
            6,
            4,
            5,
            4,
            False,  # e2-e3
        )
        assert notation == "e3"

        # Pawn capture
        notation = ChessEngine.get_chess_notation(
            PieceType.PAWN,
            6,
            4,
            5,
            5,
            True,  # exf3
        )
        assert notation == "exf3"

    def test_piece_notation(self):
        """Test piece move notation."""
        # Knight move
        notation = ChessEngine.get_chess_notation(
            PieceType.KNIGHT,
            7,
            1,
            5,
            2,
            False,  # Nc3
        )
        assert notation == "Nc3"

        # Rook capture
        notation = ChessEngine.get_chess_notation(
            PieceType.ROOK,
            7,
            0,
            7,
            4,
            True,  # Rxe1
        )
        assert notation == "Rxe1"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
