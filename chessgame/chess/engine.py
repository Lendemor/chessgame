"""Chess game engine with move validation and game logic."""

from .pieces import Piece, PieceType, PlayerType, NO_PIECE
from .board import find_king

COL_NOTATION = "abcdefgh"


class ChessEngine:
    """Chess game engine for move validation and game logic."""

    @staticmethod
    def is_valid_move(
        grid: list[list[Piece]],
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        en_passant_target: tuple[int, int] | None = None,
    ) -> bool:
        """Validates if a move is legal according to chess rules."""
        # Bounds check
        if not (0 <= to_row < 8 and 0 <= to_col < 8):
            return False

        piece = grid[from_row][from_col]
        if piece.type == PieceType.NONE:
            return False

        # Can't move to same square
        if from_row == to_row and from_col == to_col:
            return False

        # Can't move to square occupied by own piece
        destination_piece = grid[to_row][to_col]
        if (
            destination_piece.type != PieceType.NONE
            and destination_piece.owner == piece.owner
        ):
            return False

        # Piece-specific validation
        if piece.type == PieceType.PAWN:
            return ChessEngine._is_valid_pawn_move(
                grid, from_row, from_col, to_row, to_col, piece.owner, en_passant_target
            )
        elif piece.type == PieceType.ROOK:
            return ChessEngine._is_valid_rook_move(
                grid, from_row, from_col, to_row, to_col
            )
        elif piece.type == PieceType.BISHOP:
            return ChessEngine._is_valid_bishop_move(
                grid, from_row, from_col, to_row, to_col
            )
        elif piece.type == PieceType.KNIGHT:
            return ChessEngine._is_valid_knight_move(
                grid, from_row, from_col, to_row, to_col
            )
        elif piece.type == PieceType.QUEEN:
            return ChessEngine._is_valid_queen_move(
                grid, from_row, from_col, to_row, to_col
            )
        elif piece.type == PieceType.KING:
            # Check for castling first
            if ChessEngine.is_castling_move(grid, from_row, from_col, to_row, to_col):
                # Castling validation will be handled separately in the UI layer
                return True
            else:
                return ChessEngine._is_valid_king_move(
                    grid, from_row, from_col, to_row, to_col
                )

        return False

    @staticmethod
    def _is_valid_pawn_move(
        grid: list[list[Piece]],
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        owner: PlayerType,
        en_passant_target: tuple[int, int] | None = None,
    ) -> bool:
        """Validates pawn moves."""
        direction = (
            -1 if owner == PlayerType.WHITE else 1
        )  # White moves up (negative), Black moves down (positive)
        start_row = 6 if owner == PlayerType.WHITE else 1

        # Forward moves
        if from_col == to_col:
            # One square forward
            if to_row == from_row + direction:
                return grid[to_row][to_col].type == PieceType.NONE
            # Two squares forward from starting position
            elif from_row == start_row and to_row == from_row + 2 * direction:
                return (
                    grid[to_row][to_col].type == PieceType.NONE
                    and grid[from_row + direction][to_col].type == PieceType.NONE
                )

        # Diagonal captures
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target_piece = grid[to_row][to_col]

            # Regular diagonal capture
            if target_piece.type != PieceType.NONE and target_piece.owner != owner:
                return True

            # En passant capture
            if (
                en_passant_target is not None
                and (to_row, to_col) == en_passant_target
                and target_piece.type == PieceType.NONE
            ):
                return True

        return False

    @staticmethod
    def _is_valid_rook_move(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates rook moves (horizontal/vertical)."""
        # Must move in straight line
        if from_row != to_row and from_col != to_col:
            return False

        return ChessEngine._is_path_clear(grid, from_row, from_col, to_row, to_col)

    @staticmethod
    def _is_valid_bishop_move(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates bishop moves (diagonal)."""
        # Must move diagonally
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False

        return ChessEngine._is_path_clear(grid, from_row, from_col, to_row, to_col)

    @staticmethod
    def _is_valid_knight_move(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates knight moves (L-shape)."""
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)

        # L-shape: 2+1 or 1+2
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    @staticmethod
    def _is_valid_queen_move(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates queen moves (combination of rook and bishop)."""
        return ChessEngine._is_valid_rook_move(
            grid, from_row, from_col, to_row, to_col
        ) or ChessEngine._is_valid_bishop_move(grid, from_row, from_col, to_row, to_col)

    @staticmethod
    def _is_valid_king_move(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validates king moves (one square in any direction)."""
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)

        # One square in any direction
        return row_diff <= 1 and col_diff <= 1

    @staticmethod
    def _is_path_clear(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Checks if path between two squares is clear (excluding endpoints)."""
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)

        current_row = from_row + row_step
        current_col = from_col + col_step

        while current_row != to_row or current_col != to_col:
            if grid[current_row][current_col].type != PieceType.NONE:
                return False
            current_row += row_step
            current_col += col_step

        return True

    @staticmethod
    def is_square_under_attack(
        grid: list[list[Piece]], row: int, col: int, by_player: PlayerType
    ) -> bool:
        """Check if a square is under attack by any piece of the given player."""
        for attack_row in range(8):
            for attack_col in range(8):
                piece = grid[attack_row][attack_col]

                # Skip empty squares and pieces not owned by the attacking player
                if piece.type == PieceType.NONE or piece.owner != by_player:
                    continue

                # Check if this piece can attack the target square
                if ChessEngine.is_valid_move(grid, attack_row, attack_col, row, col):
                    return True

        return False

    @staticmethod
    def is_in_check(grid: list[list[Piece]], player: PlayerType) -> bool:
        """Check if the given player's king is in check."""
        king_pos = find_king(grid, player)
        if king_pos is None:
            return False  # No king found (shouldn't happen in normal game)

        king_row, king_col = king_pos
        enemy_player = (
            PlayerType.BLACK if player == PlayerType.WHITE else PlayerType.WHITE
        )

        return ChessEngine.is_square_under_attack(
            grid, king_row, king_col, enemy_player
        )

    @staticmethod
    def would_leave_king_in_check(
        grid: list[list[Piece]],
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        player: PlayerType,
    ) -> bool:
        """Check if a move would leave the player's king in check."""
        # Save the current state
        original_piece = grid[from_row][from_col]
        captured_piece = grid[to_row][to_col]

        # Temporarily make the move
        grid[to_row][to_col] = original_piece
        grid[from_row][from_col] = NO_PIECE

        # Check if king is in check after the move
        king_in_check = ChessEngine.is_in_check(grid, player)

        # Restore the original state
        grid[from_row][from_col] = original_piece
        grid[to_row][to_col] = captured_piece

        return king_in_check

    @staticmethod
    def is_castling_move(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Check if this is a castling move (king moving 2 squares horizontally)."""
        piece = grid[from_row][from_col]
        if piece.type != PieceType.KING:
            return False

        # King moving 2 squares horizontally on same row
        return from_row == to_row and abs(from_col - to_col) == 2

    @staticmethod
    def is_valid_castling(
        grid: list[list[Piece]],
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        player: PlayerType,
        king_moved: bool,
        kingside_rook_moved: bool,
        queenside_rook_moved: bool,
    ) -> bool:
        """Validates castling moves."""
        piece = grid[from_row][from_col]

        # Must be a king
        if piece.type != PieceType.KING or piece.owner != player:
            return False

        # King must not have moved
        if king_moved:
            return False

        # Must be moving 2 squares horizontally
        if from_row != to_row or abs(from_col - to_col) != 2:
            return False

        # Determine if kingside or queenside castling
        is_kingside = to_col > from_col

        # Check if corresponding rook has moved
        if is_kingside and kingside_rook_moved:
            return False
        if not is_kingside and queenside_rook_moved:
            return False

        # Get rook position
        rook_col = 7 if is_kingside else 0
        rook = grid[from_row][rook_col]

        # Rook must be present and not moved
        if rook.type != PieceType.ROOK or rook.owner != player:
            return False

        # Path between king and rook must be clear
        start_col = min(from_col, rook_col) + 1
        end_col = max(from_col, rook_col)
        for col in range(start_col, end_col):
            if grid[from_row][col].type != PieceType.NONE:
                return False

        # King must not be in check
        if ChessEngine.is_in_check(grid, player):
            return False

        # King must not pass through or end in check
        direction = 1 if is_kingside else -1
        for i in range(1, 3):  # Check squares king passes through and lands on
            test_col = from_col + (i * direction)

            # Temporarily move king to test square
            original_king = grid[from_row][from_col]
            grid[from_row][from_col] = NO_PIECE
            grid[from_row][test_col] = original_king

            # Check if king would be in check
            in_check = ChessEngine.is_in_check(grid, player)

            # Restore original position
            grid[from_row][from_col] = original_king
            grid[from_row][test_col] = NO_PIECE

            if in_check:
                return False

        return True

    @staticmethod
    def is_en_passant_move(
        grid: list[list[Piece]],
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        en_passant_target: tuple[int, int] | None,
    ) -> bool:
        """Check if this is an en passant capture."""
        piece = grid[from_row][from_col]

        # Must be a pawn
        if piece.type != PieceType.PAWN:
            return False

        # Must be capturing diagonally to empty square
        if (
            abs(from_col - to_col) == 1
            and grid[to_row][to_col].type == PieceType.NONE
            and en_passant_target is not None
            and (to_row, to_col) == en_passant_target
        ):
            return True

        return False

    @staticmethod
    def get_en_passant_target(
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        piece_type: PieceType,
        owner: PlayerType,
    ) -> tuple[int, int] | None:
        """Get en passant target square if pawn moved 2 squares."""
        # Only pawns can create en passant targets
        if piece_type != PieceType.PAWN:
            return None

        # Must be moving 2 squares forward
        if abs(from_row - to_row) != 2 or from_col != to_col:
            return None

        # Must be from starting position
        if owner == PlayerType.WHITE and from_row != 6:
            return None
        if owner == PlayerType.BLACK and from_row != 1:
            return None

        # En passant target is the square the pawn "jumped over"
        target_row = (from_row + to_row) // 2
        return (target_row, from_col)

    @staticmethod
    def is_pawn_promotion(
        from_row: int, to_row: int, piece_type: PieceType, owner: PlayerType
    ) -> bool:
        """Check if a pawn move results in promotion."""
        if piece_type != PieceType.PAWN:
            return False

        # White pawns promote when reaching row 0 (rank 8)
        if owner == PlayerType.WHITE and to_row == 0:
            return True

        # Black pawns promote when reaching row 7 (rank 1)
        if owner == PlayerType.BLACK and to_row == 7:
            return True

        return False

    @staticmethod
    def get_chess_notation(
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

    @staticmethod
    def get_all_legal_moves(
        grid: list[list[Piece]],
        player: PlayerType,
        en_passant_target: tuple[int, int] | None = None,
    ) -> list[tuple[int, int, int, int]]:
        """Get all legal moves for a player (moves that don't leave king in check)."""
        legal_moves = []

        for from_row in range(8):
            for from_col in range(8):
                piece = grid[from_row][from_col]

                # Skip empty squares and opponent pieces
                if piece.type == PieceType.NONE or piece.owner != player:
                    continue

                # Check all possible destination squares
                for to_row in range(8):
                    for to_col in range(8):
                        # Check if the move is valid according to piece rules
                        if ChessEngine.is_valid_move(
                            grid, from_row, from_col, to_row, to_col, en_passant_target
                        ):
                            # Check if move would leave king in check
                            if not ChessEngine.would_leave_king_in_check(
                                grid, from_row, from_col, to_row, to_col, player
                            ):
                                legal_moves.append((from_row, from_col, to_row, to_col))

        return legal_moves

    @staticmethod
    def is_checkmate(
        grid: list[list[Piece]],
        player: PlayerType,
        en_passant_target: tuple[int, int] | None = None,
    ) -> bool:
        """Check if the given player is in checkmate."""
        # Must be in check to be checkmate
        if not ChessEngine.is_in_check(grid, player):
            return False

        # If in check and no legal moves, it's checkmate
        legal_moves = ChessEngine.get_all_legal_moves(grid, player, en_passant_target)
        return len(legal_moves) == 0

    @staticmethod
    def is_stalemate(
        grid: list[list[Piece]],
        player: PlayerType,
        en_passant_target: tuple[int, int] | None = None,
    ) -> bool:
        """Check if the given player is in stalemate."""
        # Must NOT be in check to be stalemate
        if ChessEngine.is_in_check(grid, player):
            return False

        # If not in check and no legal moves, it's stalemate
        legal_moves = ChessEngine.get_all_legal_moves(grid, player, en_passant_target)
        return len(legal_moves) == 0
