# ============================================================
# CalcScript Lexer — A math-first programming language
# ============================================================

# ── Token Types ──────────────────────────────────────────────
# Each constant defines a distinct token category the lexer
# can produce.  Keeping them as plain strings makes debugging
# and testing straightforward.

TOKEN_NUMBER     = "NUMBER"
TOKEN_IDENTIFIER = "IDENTIFIER"
TOKEN_PLUS       = "PLUS"
TOKEN_MINUS      = "MINUS"
TOKEN_MUL        = "MUL"
TOKEN_DIV        = "DIV"
TOKEN_EQUALS     = "EQUALS"
TOKEN_LPAREN     = "LPAREN"
TOKEN_RPAREN     = "RPAREN"
TOKEN_EOF        = "EOF"

# Keywords are matched *after* an identifier is read, so the
# lexer first treats every letter-sequence as an IDENTIFIER
# and then promotes it to a keyword token when applicable.
KEYWORDS = {
    "let":   "LET",
    "print": "PRINT",
}


# ── Token ────────────────────────────────────────────────────
class Token:
    """Smallest meaningful unit produced by the lexer.

    Attributes
    ----------
    type  : str   – one of the TOKEN_* constants or a keyword name
    value : any   – the raw Python value (int/float for numbers,
                    str for identifiers & operators)
    """

    def __init__(self, type: str, value):
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r})"


# ── Lexer ────────────────────────────────────────────────────
class Lexer:
    """Deterministic, single-pass scanner for CalcScript source.

    Usage
    -----
        tokens = Lexer("let x = 10 + 5").tokenize()

    The returned list always ends with a sentinel ``Token(EOF, None)``
    so downstream consumers (parser, evaluator) can rely on a clean
    termination signal.
    """

    def __init__(self, source: str):
        self.source = source
        self.pos = 0           # current index into `source`
        self.tokens: list[Token] = []

    # ── helpers ──────────────────────────────────────────────
    def _current_char(self) -> str | None:
        """Return the character at ``self.pos``, or None at EOF."""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def _advance(self) -> None:
        """Move the cursor forward by one character."""
        self.pos += 1

    # ── number literal  (integers & floats) ──────────────────
    def _read_number(self) -> Token:
        """Consume a contiguous numeric literal.

        Supports integers (``42``) and floating-point values
        (``3.14``).  Only a single decimal point is allowed.
        """
        start = self.pos
        has_dot = False

        while self._current_char() is not None and (
            self._current_char().isdigit() or self._current_char() == "."
        ):
            if self._current_char() == ".":
                if has_dot:
                    break            # second dot → stop here
                has_dot = True
            self._advance()

        text = self.source[start : self.pos]
        value = float(text) if has_dot else int(text)
        return Token(TOKEN_NUMBER, value)

    # ── identifier / keyword ─────────────────────────────────
    def _read_identifier(self) -> Token:
        """Consume an identifier (letter/underscore start, then
        letters, digits, or underscores).  If the resulting text
        matches a keyword it is promoted automatically.
        """
        start = self.pos

        while self._current_char() is not None and (
            self._current_char().isalnum() or self._current_char() == "_"
        ):
            self._advance()

        text = self.source[start : self.pos]

        # Check if the identifier is a reserved keyword
        token_type = KEYWORDS.get(text.lower(), TOKEN_IDENTIFIER)
        return Token(token_type, text)

    # ── main driver ──────────────────────────────────────────
    def tokenize(self) -> list[Token]:
        """Scan the entire source string and return a list of Tokens."""

        while self._current_char() is not None:
            ch = self._current_char()

            # Skip whitespace (spaces, tabs, newlines)
            if ch in (" ", "\t", "\n", "\r"):
                self._advance()
                continue

            # Numbers
            if ch.isdigit():
                self.tokens.append(self._read_number())
                continue

            # Identifiers & keywords
            if ch.isalpha() or ch == "_":
                self.tokens.append(self._read_identifier())
                continue

            # Single-character operators & syntax
            if ch == "#":
                while self._current_char() is not None and self._current_char() != "\n":
                    self._advance()
                continue

            if ch == "+":
                self.tokens.append(Token(TOKEN_PLUS, "+"))
                self._advance()
            elif ch == "-":
                self.tokens.append(Token(TOKEN_MINUS, "-"))
                self._advance()
            elif ch == "*":
                self.tokens.append(Token(TOKEN_MUL, "*"))
                self._advance()
            elif ch == "/":
                self.tokens.append(Token(TOKEN_DIV, "/"))
                self._advance()
            elif ch == "=":
                self.tokens.append(Token(TOKEN_EQUALS, "="))
                self._advance()
            elif ch == "(":
                self.tokens.append(Token(TOKEN_LPAREN, "("))
                self._advance()
            elif ch == ")":
                self.tokens.append(Token(TOKEN_RPAREN, ")"))
                self._advance()
            else:
                raise SyntaxError(
                    f"CalcScript Lexer Error: unexpected character {ch!r} "
                    f"at position {self.pos}"
                )

        # Sentinel token so the parser knows when input ends
        self.tokens.append(Token(TOKEN_EOF, None))
        return self.tokens


# ── Quick smoke test ─────────────────────────────────────────
if __name__ == "__main__":
    source = "let x = 10 + 5 # this is a comment\nprint x"
    print(f'Source : "{source}"\n')
    print("Tokens:")
    for tok in Lexer(source).tokenize():
        print(f"  {tok}")
