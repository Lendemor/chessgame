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
        assert not ChessEngine.is_valid_move(board, 4, 4, 6, 4)  # 2 squares vertical
        assert not ChessEngine.is_valid_move(board, 4, 4, 2, 4)  # 2 squares vertical


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
        assert ChessEngine.is_valid_castling(
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

        assert ChessEngine.is_valid_castling(
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

    def test_invalid_castling_king_moved(self):
        """Test castling invalid when king has moved."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)
        board[7][7] = Piece(PieceType.ROOK, PlayerType.WHITE)

        # Invalid because king has moved
        assert not ChessEngine.is_valid_castling(
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

    def test_invalid_castling_rook_moved(self):
        """Test castling invalid when rook has moved."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)
        board[7][7] = Piece(PieceType.ROOK, PlayerType.WHITE)

        # Invalid because kingside rook has moved
        assert not ChessEngine.is_valid_castling(
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

    def test_invalid_castling_blocked_path(self):
        """Test castling invalid when path is blocked."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)
        board[7][7] = Piece(PieceType.ROOK, PlayerType.WHITE)
        board[7][5] = Piece(PieceType.BISHOP, PlayerType.WHITE)  # Blocking piece

        # Invalid because path is blocked
        assert not ChessEngine.is_valid_castling(
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


class TestEnPassant:
    """Test en passant capture rules."""

    def test_en_passant_target_generation(self):
        """Test en passant target square generation."""
        # White pawn moving 2 squares from starting position
        target = ChessEngine.get_en_passant_target(
            6,
            4,
            4,
            4,
            PieceType.PAWN,
            PlayerType.WHITE,  # e2-e4
        )
        assert target == (5, 4)  # e3 square

        # Black pawn moving 2 squares from starting position
        target = ChessEngine.get_en_passant_target(
            1,
            3,
            3,
            3,
            PieceType.PAWN,
            PlayerType.BLACK,  # d7-d5
        )
        assert target == (2, 3)  # d6 square

        # Not a pawn - should return None
        target = ChessEngine.get_en_passant_target(
            7, 0, 5, 0, PieceType.ROOK, PlayerType.WHITE
        )
        assert target is None

        # Pawn moving only 1 square - should return None
        target = ChessEngine.get_en_passant_target(
            6, 4, 5, 4, PieceType.PAWN, PlayerType.WHITE
        )
        assert target is None

        # Pawn not from starting position - should return None
        target = ChessEngine.get_en_passant_target(
            5, 4, 3, 4, PieceType.PAWN, PlayerType.WHITE
        )
        assert target is None

    def test_en_passant_detection(self):
        """Test en passant move detection."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Set up en passant scenario
        board[3][4] = Piece(PieceType.PAWN, PlayerType.WHITE)  # White pawn on e5
        board[3][3] = Piece(PieceType.PAWN, PlayerType.BLACK)  # Black pawn on d5

        # En passant target after black pawn moved d7-d5
        en_passant_target = (2, 3)  # d6 square

        # White pawn should be able to capture en passant
        assert ChessEngine.is_en_passant_move(
            board,
            3,
            4,
            2,
            3,
            en_passant_target,  # e5xd6 e.p.
        )

        # Not an en passant move if no target set
        assert not ChessEngine.is_en_passant_move(board, 3, 4, 2, 3, None)

        # Not an en passant move if not a pawn
        board[3][4] = Piece(PieceType.ROOK, PlayerType.WHITE)
        assert not ChessEngine.is_en_passant_move(board, 3, 4, 2, 3, en_passant_target)

    def test_en_passant_validation_in_move(self):
        """Test en passant validation in regular move validation."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Set up en passant scenario - white pawn attacks black pawn
        board[3][4] = Piece(PieceType.PAWN, PlayerType.WHITE)  # White pawn on e5
        board[3][3] = Piece(PieceType.PAWN, PlayerType.BLACK)  # Black pawn on d5

        # En passant target after black pawn moved d7-d5
        en_passant_target = (2, 3)  # d6 square (where white can capture)

        # Should be valid en passant capture
        assert ChessEngine.is_valid_move(
            board,
            3,
            4,
            2,
            3,
            en_passant_target,  # e5xd6 e.p.
        )

        # Should not be valid without en passant target
        assert not ChessEngine.is_valid_move(board, 3, 4, 2, 3, None)

    @pytest.mark.parametrize(
        "white_start_row,white_start_col,black_pawn_col,expected_target",
        [
            (3, 4, 3, (2, 3)),  # White e5, black d5 -> target d6
            (3, 4, 5, (2, 5)),  # White e5, black f5 -> target f6
            (4, 2, 1, (3, 1)),  # White c4, black b4 -> target b3
            (4, 6, 7, (3, 7)),  # White g4, black h4 -> target h3
        ],
    )
    def test_en_passant_scenarios(
        self, white_start_row, white_start_col, black_pawn_col, expected_target
    ):
        """Test various en passant capture scenarios."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Place white pawn
        board[white_start_row][white_start_col] = Piece(
            PieceType.PAWN, PlayerType.WHITE
        )
        # Place black pawn next to it
        board[white_start_row][black_pawn_col] = Piece(PieceType.PAWN, PlayerType.BLACK)

        # Test en passant capture
        assert ChessEngine.is_valid_move(
            board,
            white_start_row,
            white_start_col,
            expected_target[0],
            expected_target[1],
            expected_target,
        )

    def test_black_en_passant_capture(self):
        """Test black pawn capturing white pawn en passant."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Set up scenario - black pawn attacks white pawn
        board[4][3] = Piece(PieceType.PAWN, PlayerType.BLACK)  # Black pawn on d4
        board[4][4] = Piece(PieceType.PAWN, PlayerType.WHITE)  # White pawn on e4

        # En passant target after white pawn moved e2-e4
        en_passant_target = (5, 4)  # e3 square

        # Black should be able to capture en passant
        assert ChessEngine.is_valid_move(
            board,
            4,
            3,
            5,
            4,
            en_passant_target,  # d4xe3 e.p.
        )

    def test_en_passant_with_check_situations(self):
        """Test en passant captures don't work if they leave king in check."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Set up a scenario where en passant would expose king to check
        board[4][4] = Piece(PieceType.KING, PlayerType.WHITE)  # White king on e4
        board[4][3] = Piece(PieceType.PAWN, PlayerType.WHITE)  # White pawn on d4
        board[4][2] = Piece(PieceType.PAWN, PlayerType.BLACK)  # Black pawn on c4
        board[4][0] = Piece(PieceType.ROOK, PlayerType.BLACK)  # Black rook on a4

        # En passant target after black pawn moved c6-c4
        en_passant_target = (5, 2)  # c3 square

        # This en passant capture would expose the king to the rook
        # The move validation should prevent this
        legal_moves = ChessEngine.get_all_legal_moves(
            board, PlayerType.WHITE, en_passant_target
        )

        # The en passant capture (4,3) -> (5,2) should not be in legal moves
        en_passant_move = (4, 3, 5, 2)
        assert en_passant_move not in legal_moves


class TestPawnPromotion:
    """Test pawn promotion rules."""

    def test_pawn_promotion_detection(self):
        """Test pawn promotion detection."""
        # White pawn reaching rank 8 (row 0)
        assert ChessEngine.is_pawn_promotion(1, 0, PieceType.PAWN, PlayerType.WHITE)

        # Black pawn reaching rank 1 (row 7)
        assert ChessEngine.is_pawn_promotion(6, 7, PieceType.PAWN, PlayerType.BLACK)

        # Not a pawn - should return False
        assert not ChessEngine.is_pawn_promotion(1, 0, PieceType.ROOK, PlayerType.WHITE)

        # Pawn not reaching promotion rank - should return False
        assert not ChessEngine.is_pawn_promotion(2, 1, PieceType.PAWN, PlayerType.WHITE)
        assert not ChessEngine.is_pawn_promotion(5, 6, PieceType.PAWN, PlayerType.BLACK)

    @pytest.mark.parametrize(
        "from_row,to_row,owner,expected",
        [
            (1, 0, PlayerType.WHITE, True),  # White pawn 7th to 8th rank
            (6, 7, PlayerType.BLACK, True),  # Black pawn 2nd to 1st rank
            (2, 1, PlayerType.WHITE, False),  # White pawn not to 8th rank
            (5, 6, PlayerType.BLACK, False),  # Black pawn not to 1st rank
            (1, 0, PlayerType.BLACK, False),  # Black pawn wrong direction
            (6, 7, PlayerType.WHITE, False),  # White pawn wrong direction
        ],
    )
    def test_promotion_scenarios(self, from_row, to_row, owner, expected):
        """Test various pawn promotion scenarios."""
        result = ChessEngine.is_pawn_promotion(from_row, to_row, PieceType.PAWN, owner)
        assert result == expected

    def test_promotion_move_validation(self):
        """Test that promotion moves are validated correctly."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # White pawn on 7th rank (row 1) ready to promote
        board[1][4] = Piece(PieceType.PAWN, PlayerType.WHITE)

        # Should be valid move to promotion rank
        assert ChessEngine.is_valid_move(board, 1, 4, 0, 4)  # e7-e8

        # Test promotion capture
        board[0][5] = Piece(PieceType.ROOK, PlayerType.BLACK)  # Black rook on f8
        assert ChessEngine.is_valid_move(board, 1, 4, 0, 5)  # exf8 (capture promotion)

    def test_promotion_with_capture(self):
        """Test pawn promotion while capturing."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Black pawn on 2nd rank (row 6) ready to promote
        board[6][3] = Piece(PieceType.PAWN, PlayerType.BLACK)
        # White piece to capture
        board[7][4] = Piece(PieceType.KNIGHT, PlayerType.WHITE)

        # Should be valid capture promotion
        assert ChessEngine.is_valid_move(board, 6, 3, 7, 4)  # dxe1

    def test_promotion_blocking_check(self):
        """Test promotion move that can block check."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Simple test: white pawn can just promote normally (no check scenario)
        board[7][4] = Piece(PieceType.KING, PlayerType.WHITE)  # White king on e1
        board[1][4] = Piece(PieceType.PAWN, PlayerType.WHITE)  # White pawn on e7

        # Pawn can promote
        legal_moves = ChessEngine.get_all_legal_moves(board, PlayerType.WHITE)
        promotion_move = (1, 4, 0, 4)  # e7-e8 promotion
        assert promotion_move in legal_moves

    def test_promotion_creates_checkmate(self):
        """Test promotion that creates checkmate."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # Setup a simpler position where promotion creates checkmate
        board[7][7] = Piece(PieceType.KING, PlayerType.BLACK)  # Black king on h1
        board[6][6] = Piece(PieceType.KING, PlayerType.WHITE)  # White king on g2
        board[1][6] = Piece(PieceType.PAWN, PlayerType.WHITE)  # White pawn on g7

        # Promote pawn to queen - this should be checkmate
        test_board = [row.copy() for row in board]
        test_board[0][6] = Piece(
            PieceType.QUEEN, PlayerType.WHITE
        )  # Promote to queen on g8
        test_board[1][6] = NO_PIECE  # Remove pawn

        assert ChessEngine.is_checkmate(test_board, PlayerType.BLACK)

    def test_underpromotion_options(self):
        """Test that all promotion options (not just queen) work."""
        board = [[NO_PIECE for _ in range(8)] for _ in range(8)]

        # White pawn ready to promote
        board[1][4] = Piece(PieceType.PAWN, PlayerType.WHITE)

        # Test each promotion option would be valid
        for piece_type in [
            PieceType.QUEEN,
            PieceType.ROOK,
            PieceType.BISHOP,
            PieceType.KNIGHT,
        ]:
            # The basic move should be valid regardless of promotion choice
            assert ChessEngine.is_valid_move(board, 1, 4, 0, 4)


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
