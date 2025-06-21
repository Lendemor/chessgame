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

    # Pawn promotion - track if a promotion is pending
    promotion_pending: rx.Field[bool] = rx.field(default_factory=lambda: False)
    promotion_row: rx.Field[int] = rx.field(default_factory=lambda: -1)
    promotion_col: rx.Field[int] = rx.field(default_factory=lambda: -1)
    promotion_player: rx.Field[PlayerType] = rx.field(
        default_factory=lambda: PlayerType.NONE
    )

    # Move history
    move_history: rx.Field[list[str]] = rx.field(default_factory=lambda: [])

    # Draw rules tracking
    halfmove_clock: rx.Field[int] = rx.field(
        default_factory=lambda: 0
    )  # For 50-move rule
    position_history: rx.Field[list[str]] = rx.field(
        default_factory=lambda: []
    )  # For threefold repetition

    # Captured pieces tracking
    captured_white_pieces: rx.Field[list[Piece]] = rx.field(default_factory=lambda: [])
    captured_black_pieces: rx.Field[list[Piece]] = rx.field(default_factory=lambda: [])

    # Undo functionality - store board states and game states
    board_history: rx.Field[list[list[list[Piece]]]] = rx.field(
        default_factory=lambda: []
    )
    player_history: rx.Field[list[PlayerType]] = rx.field(default_factory=lambda: [])
    captured_white_history: rx.Field[list[list[Piece]]] = rx.field(
        default_factory=lambda: []
    )
    captured_black_history: rx.Field[list[list[Piece]]] = rx.field(
        default_factory=lambda: []
    )
    en_passant_history: rx.Field[list[tuple[int, int] | None]] = rx.field(
        default_factory=lambda: []
    )
    halfmove_clock_history: rx.Field[list[int]] = rx.field(default_factory=lambda: [])
    position_history_snapshots: rx.Field[list[list[str]]] = rx.field(
        default_factory=lambda: []
    )

    @rx.event
    def reset_grid(self):
        """Resets the grid to the default state."""
        self.grid = copy_board(create_default_board())
        self.current_player = PlayerType.WHITE
        self.game_over = False
        self.winner = ""
        self.move_history = []
        # Reset draw rules tracking
        self.halfmove_clock = 0
        self.position_history = []
        # Reset captured pieces
        self.captured_white_pieces = []
        self.captured_black_pieces = []
        # Reset castling rights
        self.white_king_moved = False
        self.white_kingside_rook_moved = False
        self.white_queenside_rook_moved = False
        self.black_king_moved = False
        self.black_kingside_rook_moved = False
        self.black_queenside_rook_moved = False
        # Reset en passant
        self.en_passant_target = None
        # Reset promotion
        self.promotion_pending = False
        self.promotion_row = -1
        self.promotion_col = -1
        self.promotion_player = PlayerType.NONE
        # Initialize history with starting position
        self.board_history = [copy_board(self.grid)]
        self.player_history = [PlayerType.WHITE]
        self.captured_white_history = [[]]  # Start with empty captured pieces
        self.captured_black_history = [[]]
        self.en_passant_history = [None]  # Start with no en passant target
        self.halfmove_clock_history = [0]  # Start with halfmove clock at 0
        self.position_history_snapshots = [[]]  # Start with empty position history
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
        self.captured_white_history.pop()  # Remove current captured white pieces
        self.captured_black_history.pop()  # Remove current captured black pieces
        self.en_passant_history.pop()  # Remove current en passant target
        self.halfmove_clock_history.pop()  # Remove current halfmove clock
        self.position_history_snapshots.pop()  # Remove current position history snapshot

        # Restore previous board, player, captured pieces, en passant target, and draw rule states
        self.grid = copy_board(self.board_history[-1])
        self.current_player = self.player_history[-1]
        self.captured_white_pieces = self.captured_white_history[-1].copy()
        self.captured_black_pieces = self.captured_black_history[-1].copy()
        self.en_passant_target = self.en_passant_history[-1]
        self.halfmove_clock = self.halfmove_clock_history[-1]
        self.position_history = self.position_history_snapshots[-1].copy()

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

    def is_pawn_promotion(
        self, from_row: int, to_row: int, piece_type: PieceType, owner: PlayerType
    ) -> bool:
        """Check if a pawn move results in promotion."""
        return ChessEngine.is_pawn_promotion(from_row, to_row, piece_type, owner)

    @rx.event
    def promote_pawn(self, piece_type_str: str):
        """Promote a pawn to the specified piece type."""
        if not self.promotion_pending:
            return rx.toast("No pawn promotion pending!")

        # Convert string back to enum
        piece_type = PieceType(piece_type_str)

        # Create promoted piece
        promoted_piece = Piece(piece_type, self.promotion_player)
        self.grid[self.promotion_row][self.promotion_col] = promoted_piece

        # Store promotion info before clearing state
        promotion_player = self.promotion_player

        # Clear promotion state
        self.promotion_pending = False
        self.promotion_row = -1
        self.promotion_col = -1
        self.promotion_player = PlayerType.NONE

        # Add promotion notation to move history
        if self.move_history:
            last_move = self.move_history[-1]
            piece_symbol = {
                PieceType.QUEEN: "Q",
                PieceType.ROOK: "R",
                PieceType.BISHOP: "B",
                PieceType.KNIGHT: "N",
            }.get(piece_type, "")

            # Update last move with promotion notation
            self.move_history[-1] = last_move.replace(
                "[Promotion]", f"[{piece_symbol}]"
            )

        # Update draw rules tracking - pawn promotion resets halfmove clock
        self.halfmove_clock = 0

        # Now switch turns (if validation enabled)
        if self.turn_validation_enabled:
            self.current_player = (
                PlayerType.BLACK
                if self.current_player == PlayerType.WHITE
                else PlayerType.WHITE
            )

        # Track position for threefold repetition (after turn switch)
        current_position = self.get_position_string()
        self.position_history.append(current_position)

        # Save state for undo functionality (after promotion and turn switch)
        self.board_history.append(copy_board(self.grid))
        self.player_history.append(self.current_player)
        self.captured_white_history.append(self.captured_white_pieces.copy())
        self.captured_black_history.append(self.captured_black_pieces.copy())
        self.en_passant_history.append(self.en_passant_target)
        self.halfmove_clock_history.append(self.halfmove_clock)
        self.position_history_snapshots.append(self.position_history.copy())

        # Check if the move puts the opponent in check or ends the game
        opponent = (
            PlayerType.BLACK
            if promotion_player == PlayerType.WHITE
            else PlayerType.WHITE
        )
        opponent_in_check = self.is_in_check(opponent)

        # Check for game ending conditions after the promotion
        game_ending_toast = self.check_game_ending_conditions()
        if game_ending_toast:
            return game_ending_toast

        # Show promotion success message
        check_msg = " - Check!" if opponent_in_check else ""
        return rx.toast(f"Pawn promoted to {piece_type.value}!{check_msg}")

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

    def get_position_string(self) -> str:
        """Generate a string representation of the current position for threefold repetition."""
        # Include board state, current player, castling rights, and en passant target
        position_parts = []

        # Board state
        for row in self.grid:
            row_str = ""
            for piece in row:
                if piece.type == PieceType.NONE:
                    row_str += "."
                else:
                    piece_char = piece.type.value[0].lower()
                    if piece.owner == PlayerType.WHITE:
                        piece_char = piece_char.upper()
                    row_str += piece_char
            position_parts.append(row_str)

        # Current player
        position_parts.append(f"turn:{self.current_player.value}")

        # Castling rights
        castling = ""
        if not self.white_king_moved and not self.white_kingside_rook_moved:
            castling += "K"
        if not self.white_king_moved and not self.white_queenside_rook_moved:
            castling += "Q"
        if not self.black_king_moved and not self.black_kingside_rook_moved:
            castling += "k"
        if not self.black_king_moved and not self.black_queenside_rook_moved:
            castling += "q"
        position_parts.append(f"castle:{castling}")

        # En passant target
        en_passant = (
            "none"
            if self.en_passant_target is None
            else f"{self.en_passant_target[0]},{self.en_passant_target[1]}"
        )
        position_parts.append(f"ep:{en_passant}")

        return "|".join(position_parts)

    def check_threefold_repetition(self) -> bool:
        """Check if the current position has occurred 3 times (threefold repetition)."""
        current_position = self.get_position_string()
        count = self.position_history.count(current_position)
        return count >= 2  # Current position + 2 previous = 3 total

    def check_fifty_move_rule(self) -> bool:
        """Check if 50 moves have passed without pawn move or capture."""
        return self.halfmove_clock >= 100  # 100 half-moves = 50 full moves

    def check_game_ending_conditions(self):
        """Check if the game has ended due to checkmate, stalemate, or draw rules."""
        if self.game_over:
            return  # Game already over

        # Check for draw conditions first
        if self.check_fifty_move_rule():
            self.game_over = True
            self.winner = "DRAW"
            return rx.toast("Draw by 50-move rule!")

        if self.check_threefold_repetition():
            self.game_over = True
            self.winner = "DRAW"
            return rx.toast("Draw by threefold repetition!")

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
                is_promotion = self.is_pawn_promotion(
                    source_row, row, piece_type, piece_owner
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

                # Track captured pieces for regular captures
                if (
                    is_capture
                    and not is_en_passant
                    and destination_piece.type != PieceType.NONE
                ):
                    if destination_piece.owner == PlayerType.WHITE:
                        self.captured_white_pieces.append(destination_piece)
                    else:
                        self.captured_black_pieces.append(destination_piece)

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
                    captured_pawn = self.grid[captured_pawn_row][col]

                    # Track the captured pawn
                    if captured_pawn.owner == PlayerType.WHITE:
                        self.captured_white_pieces.append(captured_pawn)
                    else:
                        self.captured_black_pieces.append(captured_pawn)

                    self.grid[captured_pawn_row][col] = NO_PIECE
                elif is_promotion:
                    # Handle pawn promotion - move pawn but don't switch turns yet
                    # Track captured piece if promoting with capture
                    if destination_piece.type != PieceType.NONE:
                        if destination_piece.owner == PlayerType.WHITE:
                            self.captured_white_pieces.append(destination_piece)
                        else:
                            self.captured_black_pieces.append(destination_piece)

                    self.grid[row][col] = moved_piece
                    self.grid[source_row][source_col] = NO_PIECE

                    # Set promotion state
                    self.promotion_pending = True
                    self.promotion_row = row
                    self.promotion_col = col
                    self.promotion_player = piece_owner
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

                # Update draw rules tracking (before switching turns)
                # 50-move rule: increment halfmove clock unless pawn move or capture
                if piece_type == PieceType.PAWN or is_capture:
                    self.halfmove_clock = 0  # Reset on pawn move or capture
                else:
                    self.halfmove_clock += 1

                # For promotion moves, show promotion dialog and don't switch turns yet
                if is_promotion:
                    # Add to move history without notation (will be updated after promotion)
                    move_count = len(self.move_history) + 1
                    move_detail = f"{move_count}. {piece_owner.value} {piece_type.value} ({source_row},{source_col})→({row},{col}) [Promotion]"
                    self.move_history.append(move_detail)

                    return rx.toast("Choose piece for pawn promotion!")

                # Switch turns (if validation enabled)
                if self.turn_validation_enabled:
                    self.current_player = (
                        PlayerType.BLACK
                        if self.current_player == PlayerType.WHITE
                        else PlayerType.WHITE
                    )

                # Track position for threefold repetition (after turn switch)
                current_position = self.get_position_string()
                self.position_history.append(current_position)

                # Save state for undo functionality (after making the move and switching turns)
                self.board_history.append(copy_board(self.grid))
                self.player_history.append(self.current_player)
                self.captured_white_history.append(self.captured_white_pieces.copy())
                self.captured_black_history.append(self.captured_black_pieces.copy())
                self.en_passant_history.append(self.en_passant_target)
                self.halfmove_clock_history.append(self.halfmove_clock)
                self.position_history_snapshots.append(self.position_history.copy())

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
                    if is_en_passant:
                        # For en passant, the captured piece is a pawn
                        captured_owner = (
                            PlayerType.BLACK
                            if piece_owner == PlayerType.WHITE
                            else PlayerType.WHITE
                        )
                        return rx.toast(
                            f"{move_notation} - Captured {captured_owner.value} pawn!{check_msg}",
                        )
                    else:
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


def promotion_dialog() -> rx.Component:
    """Modal dialog for pawn promotion piece selection."""
    return rx.cond(
        ChessState.promotion_pending,
        # Modal overlay backdrop
        rx.box(
            # Backdrop blur effect
            rx.box(
                width="100vw",
                height="100vh",
                position="fixed",
                top="0",
                left="0",
                background="linear-gradient(135deg, rgba(0,0,0,0.6), rgba(30,30,60,0.8))",
                backdrop_filter="blur(5px)",
                z_index="1000",
            ),
            # Modal content container
            rx.center(
                rx.vstack(
                    # Header section with crown icon
                    rx.vstack(
                        rx.box(
                            "👑",
                            font_size="48px",
                            margin_bottom="16px",
                        ),
                        rx.heading(
                            "Pawn Promotion",
                            size="9",
                            text_align="center",
                            color="#ffffff",
                            font_weight="700",
                            letter_spacing="-0.5px",
                        ),
                        rx.text(
                            "Choose your piece wisely",
                            font_size="18px",
                            text_align="center",
                            color="#cccccc",
                            font_weight="500",
                            margin_bottom="24px",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    # Piece selection - single row with proper spacing
                    rx.hstack(
                        # Queen - Golden option
                        rx.box(
                            rx.button(
                                rx.vstack(
                                    rx.box(
                                        rx.image(
                                            src=f"{pixel_piece_folder}{ChessState.promotion_player}_queen.png",
                                            width="70px",
                                            height="70px",
                                            object_fit="contain",
                                        ),
                                        padding="10px",
                                        border_radius="12px",
                                        background="linear-gradient(145deg, rgba(255, 249, 230, 0.9), rgba(240, 230, 204, 0.9))",
                                        border="2px solid #ffd700",
                                        box_shadow="0 4px 15px rgba(255, 215, 0, 0.4)",
                                    ),
                                    rx.text(
                                        "Queen",
                                        font_weight="bold",
                                        font_size="13px",
                                        color="#ffd700",
                                        margin_top="6px",
                                    ),
                                    rx.text(
                                        "Most Powerful",
                                        font_size="9px",
                                        color="#bbb",
                                        font_style="italic",
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                                on_click=lambda: ChessState.promote_pawn("queen"),
                                background="transparent",
                                border="none",
                                padding="12px",
                                border_radius="12px",
                                _hover={
                                    "background": "rgba(255, 215, 0, 0.15)",
                                    "transform": "translateY(-3px) scale(1.02)",
                                },
                                transition="all 0.3s ease",
                                cursor="pointer",
                                width="130px",
                                height="140px",
                            ),
                            flex_shrink="0",
                        ),
                        # Rook - Strong option
                        rx.box(
                            rx.button(
                                rx.vstack(
                                    rx.box(
                                        rx.image(
                                            src=f"{pixel_piece_folder}{ChessState.promotion_player}_rook.png",
                                            width="70px",
                                            height="70px",
                                            object_fit="contain",
                                        ),
                                        padding="10px",
                                        border_radius="12px",
                                        background="linear-gradient(145deg, rgba(232, 244, 253, 0.9), rgba(209, 233, 246, 0.9))",
                                        border="2px solid #2196F3",
                                        box_shadow="0 4px 15px rgba(33, 150, 243, 0.3)",
                                    ),
                                    rx.text(
                                        "Rook",
                                        font_weight="bold",
                                        font_size="13px",
                                        color="#4fc3f7",
                                        margin_top="6px",
                                    ),
                                    rx.text(
                                        "Castle Power",
                                        font_size="9px",
                                        color="#bbb",
                                        font_style="italic",
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                                on_click=lambda: ChessState.promote_pawn("rook"),
                                background="transparent",
                                border="none",
                                padding="12px",
                                border_radius="12px",
                                _hover={
                                    "background": "rgba(33, 150, 243, 0.15)",
                                    "transform": "translateY(-3px) scale(1.02)",
                                },
                                transition="all 0.3s ease",
                                cursor="pointer",
                                width="130px",
                                height="140px",
                            ),
                            flex_shrink="0",
                        ),
                        # Bishop - Elegant option
                        rx.box(
                            rx.button(
                                rx.vstack(
                                    rx.box(
                                        rx.image(
                                            src=f"{pixel_piece_folder}{ChessState.promotion_player}_bishop.png",
                                            width="70px",
                                            height="70px",
                                            object_fit="contain",
                                        ),
                                        padding="10px",
                                        border_radius="12px",
                                        background="linear-gradient(145deg, rgba(243, 229, 245, 0.9), rgba(225, 190, 231, 0.9))",
                                        border="2px solid #9C27B0",
                                        box_shadow="0 4px 15px rgba(156, 39, 176, 0.3)",
                                    ),
                                    rx.text(
                                        "Bishop",
                                        font_weight="bold",
                                        font_size="13px",
                                        color="#ba68c8",
                                        margin_top="6px",
                                    ),
                                    rx.text(
                                        "Diagonal Force",
                                        font_size="9px",
                                        color="#bbb",
                                        font_style="italic",
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                                on_click=lambda: ChessState.promote_pawn("bishop"),
                                background="transparent",
                                border="none",
                                padding="12px",
                                border_radius="12px",
                                _hover={
                                    "background": "rgba(156, 39, 176, 0.15)",
                                    "transform": "translateY(-3px) scale(1.02)",
                                },
                                transition="all 0.3s ease",
                                cursor="pointer",
                                width="130px",
                                height="140px",
                            ),
                            flex_shrink="0",
                        ),
                        # Knight - Tactical option
                        rx.box(
                            rx.button(
                                rx.vstack(
                                    rx.box(
                                        rx.image(
                                            src=f"{pixel_piece_folder}{ChessState.promotion_player}_knight.png",
                                            width="70px",
                                            height="70px",
                                            object_fit="contain",
                                        ),
                                        padding="10px",
                                        border_radius="12px",
                                        background="linear-gradient(145deg, rgba(255, 243, 224, 0.9), rgba(255, 224, 178, 0.9))",
                                        border="2px solid #FF9800",
                                        box_shadow="0 4px 15px rgba(255, 152, 0, 0.3)",
                                    ),
                                    rx.text(
                                        "Knight",
                                        font_weight="bold",
                                        font_size="13px",
                                        color="#ffb74d",
                                        margin_top="6px",
                                    ),
                                    rx.text(
                                        "L-Shape Master",
                                        font_size="9px",
                                        color="#bbb",
                                        font_style="italic",
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                                on_click=lambda: ChessState.promote_pawn("knight"),
                                background="transparent",
                                border="none",
                                padding="12px",
                                border_radius="12px",
                                _hover={
                                    "background": "rgba(255, 152, 0, 0.15)",
                                    "transform": "translateY(-3px) scale(1.02)",
                                },
                                transition="all 0.3s ease",
                                cursor="pointer",
                                width="130px",
                                height="140px",
                            ),
                            flex_shrink="0",
                        ),
                        spacing="5",
                        justify="center",
                        align="center",
                        flex_wrap="nowrap",
                    ),
                    spacing="6",
                    align="center",
                    background="linear-gradient(145deg, #2a2a2a, #1e1e1e)",
                    padding="40px",
                    border_radius="20px",
                    box_shadow="0 20px 60px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.1)",
                    border="1px solid rgba(255, 255, 255, 0.1)",
                    max_width="700px",
                    margin="auto",
                ),
                width="100vw",
                height="100vh",
                position="fixed",
                top="0",
                left="0",
                z_index="1001",
                padding="20px",
            ),
        ),
        rx.box(),  # Empty box when not promoting
    )


def debug_panel() -> rx.Component:
    """Debug panel with game controls and move history."""
    return rx.vstack(
        rx.heading("Game Controls", size="6", color="#ffffff"),
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
                    rx.text(
                        "Current Player: ", ChessState.current_player, color="#e0e0e0"
                    ),
                    rx.cond(
                        ChessState.current_player_in_check,
                        rx.text("IN CHECK!", color="#ff5722", font_weight="bold"),
                        rx.text(""),
                    ),
                    spacing="1",
                    align="start",
                ),
            ),
            spacing="2",
            align="start",
            padding="4",
            border="1px solid #444",
            border_radius="8px",
            background_color="#2a2a2a",
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
        # Move history - Dark theme
        rx.vstack(
            rx.hstack(
                rx.heading("Move History", size="5", color="#ffffff"),
                rx.button(
                    "Copy History",
                    on_click=ChessState.copy_move_history,
                    size="2",
                    background_color="#3f51b5",
                    color="white",
                    _hover={"background_color": "#303f9f"},
                    border_radius="6px",
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
                        move,
                        font_size="sm",
                        font_family="monospace",
                        color="#e0e0e0",
                        padding_y="1",
                        _hover={"background_color": "rgba(255, 255, 255, 0.05)"},
                        border_radius="2px",
                        padding_x="2",
                    ),
                ),
                height="300px",
                overflow_y="auto",
                border="1px solid #444",
                border_radius="8px",
                padding="3",
                width="100%",
                background_color="#1a1a1a",
                box_shadow="inset 0 2px 4px rgba(0, 0, 0, 0.3)",
            ),
            spacing="2",
            width="100%",
        ),
        spacing="4",
        align="start",
        width="350px",
        padding="4",
    )


def captured_pieces_panel() -> rx.Component:
    """Panel showing captured pieces for both players."""
    return rx.vstack(
        rx.heading("Captured Pieces", size="6", color="#ffffff"),
        # White captured pieces (captured by Black)
        rx.vstack(
            rx.hstack(
                rx.text(
                    "White Lost:", font_weight="bold", color="#e0e0e0", font_size="sm"
                ),
                rx.text(
                    ChessState.captured_white_pieces.length(),
                    color="#ff6b6b",
                    font_weight="bold",
                    font_size="sm",
                ),
                spacing="2",
                align="center",
            ),
            rx.box(
                rx.foreach(
                    ChessState.captured_white_pieces,
                    lambda piece: rx.image(
                        src=f"{pixel_piece_folder}{piece.owner}_{piece.type}.png",
                        width="30px",
                        height="30px",
                        object_fit="contain",
                        margin="2px",
                    ),
                ),
                display="flex",
                flex_wrap="wrap",
                gap="2px",
                padding="3",
                border="1px solid #444",
                border_radius="6px",
                background_color="#2a2a2a",
                min_height="50px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        # Black captured pieces (captured by White)
        rx.vstack(
            rx.hstack(
                rx.text(
                    "Black Lost:", font_weight="bold", color="#e0e0e0", font_size="sm"
                ),
                rx.text(
                    ChessState.captured_black_pieces.length(),
                    color="#ff6b6b",
                    font_weight="bold",
                    font_size="sm",
                ),
                spacing="2",
                align="center",
            ),
            rx.box(
                rx.foreach(
                    ChessState.captured_black_pieces,
                    lambda piece: rx.image(
                        src=f"{pixel_piece_folder}{piece.owner}_{piece.type}.png",
                        width="30px",
                        height="30px",
                        object_fit="contain",
                        margin="2px",
                    ),
                ),
                display="flex",
                flex_wrap="wrap",
                gap="2px",
                padding="3",
                border="1px solid #444",
                border_radius="6px",
                background_color="#2a2a2a",
                min_height="50px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        spacing="4",
        align="start",
        width="320px",
        padding="4",
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.fragment(
        rx.container(
            rx.vstack(
                rx.heading("Chess Game", class_name="text-3xl", text_align="center"),
                rx.hstack(
                    # Left side - Chessboard
                    rx.vstack(
                        chessboard(),
                        align="center",
                    ),
                    # Middle - Captured pieces panel
                    captured_pieces_panel(),
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
        ),
        # Promotion modal dialog (appears on top when needed)
        promotion_dialog(),
    )


app = rxe.App()
app.add_page(index)
