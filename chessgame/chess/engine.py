"""Chess game engine with move validation and game logic."""

from .pieces import Piece, PieceType, PlayerType, NO_PIECE
from .board import find_king

COL_NOTATION = "ABCDEFGH"


class ChessEngine:
    """Chess game engine for move validation and game logic."""

    @staticmethod
    def is_valid_move(
        grid: list[list[Piece]], from_row: int, from_col: int, to_row: int, to_col: int
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
        if destination_piece.type != PieceType.NONE and destination_piece.owner == piece.owner:
            return False

        # Piece-specific validation
        if piece.type == PieceType.PAWN:
            return ChessEngine._is_valid_pawn_move(
                grid, from_row, from_col, to_row, to_col, piece.owner
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
            return target_piece.type != PieceType.NONE and target_piece.owner != owner

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
    def get_all_legal_moves(grid: list[list[Piece]], player: PlayerType) -> list[tuple[int, int, int, int]]:
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
                        if ChessEngine.is_valid_move(grid, from_row, from_col, to_row, to_col):
                            # Check if move would leave king in check
                            if not ChessEngine.would_leave_king_in_check(
                                grid, from_row, from_col, to_row, to_col, player
                            ):
                                legal_moves.append((from_row, from_col, to_row, to_col))
        
        return legal_moves

    @staticmethod
    def is_checkmate(grid: list[list[Piece]], player: PlayerType) -> bool:
        """Check if the given player is in checkmate."""
        # Must be in check to be checkmate
        if not ChessEngine.is_in_check(grid, player):
            return False
        
        # If in check and no legal moves, it's checkmate
        legal_moves = ChessEngine.get_all_legal_moves(grid, player)
        return len(legal_moves) == 0

    @staticmethod
    def is_stalemate(grid: list[list[Piece]], player: PlayerType) -> bool:
        """Check if the given player is in stalemate."""
        # Must NOT be in check to be stalemate
        if ChessEngine.is_in_check(grid, player):
            return False
        
        # If not in check and no legal moves, it's stalemate
        legal_moves = ChessEngine.get_all_legal_moves(grid, player)
        return len(legal_moves) == 0
