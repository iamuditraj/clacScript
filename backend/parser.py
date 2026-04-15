# ============================================================
# CalcScript Parser — Recursive Descent with strict math
#                      order-of-operations
# ============================================================

from lexer import (
    Lexer,
    Token,
    TOKEN_NUMBER,
    TOKEN_IDENTIFIER,
    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_MUL,
    TOKEN_DIV,
    TOKEN_EQUALS,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_EOF,
)


# ── AST Node Classes ────────────────────────────────────────

class NumberNode:
    """Literal numeric value (int or float)."""

    def __init__(self, value):
        self.value = value

    def __repr__(self) -> str:
        return f"NumberNode({self.value})"


class VarAccessNode:
    """Read access to an existing variable by name."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"VarAccessNode({self.name!r})"


class VarInitNode:
    """Variable *initialisation* via the ``let`` keyword.

    Example: ``let x = 10 + 5``
    """

    def __init__(self, name: str, value_node):
        self.name = name
        self.value_node = value_node

    def __repr__(self) -> str:
        return f"VarInitNode({self.name!r}, {self.value_node})"


class VarAssignNode:
    """Re-assignment of an already-declared variable.

    Example: ``x = 20``
    """

    def __init__(self, name: str, value_node):
        self.name = name
        self.value_node = value_node

    def __repr__(self) -> str:
        return f"VarAssignNode({self.name!r}, {self.value_node})"


class BinOpNode:
    """Binary arithmetic operation.

    Stores the left operand, the operator token, and the right
    operand.  The tree structure naturally encodes precedence:
    higher-precedence nodes sit deeper in the tree.
    """

    def __init__(self, left, op: Token, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"BinOpNode({self.left}, {self.op.value!r}, {self.right})"


class PrintNode:
    """``print <expr>`` statement."""

    def __init__(self, expr_node):
        self.expr_node = expr_node

    def __repr__(self) -> str:
        return f"PrintNode({self.expr_node})"


# ── Parser ──────────────────────────────────────────────────

class Parser:
    """Recursive-descent parser for CalcScript.

    Grammar (informal)
    -------------------
        program    → statement*
        statement  → let_stmt | assign_stmt | print_stmt | expr
        let_stmt   → LET IDENTIFIER EQUALS expr
        assign_stmt→ IDENTIFIER EQUALS expr
        print_stmt → PRINT expr
        expr       → term ((PLUS | MINUS) term)*
        term       → factor ((MUL | DIV) factor)*
        factor     → NUMBER | IDENTIFIER | LPAREN expr RPAREN
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # ── helpers ──────────────────────────────────────────────

    def _current_token(self) -> Token:
        """Return the token under the cursor."""
        return self.tokens[self.pos]

    def _peek(self, offset: int = 1) -> Token | None:
        """Look ahead by *offset* positions without consuming."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def _consume(self, expected_type: str) -> Token:
        """Consume the current token if it matches *expected_type*,
        otherwise raise a clear syntax error."""
        token = self._current_token()
        if token.type != expected_type:
            raise SyntaxError(
                f"CalcScript Parser Error: expected {expected_type}, "
                f"got {token.type} ({token.value!r}) at position {self.pos}"
            )
        self.pos += 1
        return token

    # ── expression hierarchy (lowest → highest precedence) ───

    def _parse_expression(self):
        """expr → term ((PLUS | MINUS) term)*

        Addition and subtraction — lowest arithmetic precedence.
        """
        node = self._parse_term()

        while self._current_token().type in (TOKEN_PLUS, TOKEN_MINUS):
            op = self._current_token()
            self.pos += 1
            right = self._parse_term()
            node = BinOpNode(node, op, right)

        return node

    def _parse_term(self):
        """term → factor ((MUL | DIV) factor)*

        Multiplication and division — higher arithmetic precedence.
        """
        node = self._parse_factor()

        while self._current_token().type in (TOKEN_MUL, TOKEN_DIV):
            op = self._current_token()
            self.pos += 1
            right = self._parse_factor()
            node = BinOpNode(node, op, right)

        return node

    def _parse_factor(self):
        """factor → NUMBER | IDENTIFIER | LPAREN expr RPAREN

        Highest precedence: literals, variable reads, and
        parenthesised sub-expressions.
        """
        token = self._current_token()

        # Numeric literal
        if token.type == TOKEN_NUMBER:
            self.pos += 1
            return NumberNode(token.value)

        # Variable access
        if token.type == TOKEN_IDENTIFIER:
            self.pos += 1
            return VarAccessNode(token.value)

        # Parenthesised expression
        if token.type == TOKEN_LPAREN:
            self.pos += 1                           # skip '('
            node = self._parse_expression()
            self._consume(TOKEN_RPAREN)             # skip ')'
            return node

        raise SyntaxError(
            f"CalcScript Parser Error: unexpected token {token.type} "
            f"({token.value!r}) at position {self.pos}"
        )

    # ── statement-level parsing ──────────────────────────────

    def _parse_statement(self):
        """Dispatch to the correct statement form based on the
        current token.

        • LET IDENTIFIER EQUALS expr  →  VarInitNode
        • IDENTIFIER EQUALS expr      →  VarAssignNode
        • PRINT expr                  →  PrintNode
        • anything else               →  bare expression
        """
        token = self._current_token()

        # ── let x = <expr> ──────────────────────────────────
        if token.type == "LET":
            self.pos += 1                                   # consume LET
            name_token = self._consume(TOKEN_IDENTIFIER)    # variable name
            self._consume(TOKEN_EQUALS)                     # '='
            value_node = self._parse_expression()
            return VarInitNode(name_token.value, value_node)

        # ── x = <expr>  (re-assignment) ─────────────────────
        if token.type == TOKEN_IDENTIFIER:
            # Only treat as assignment when followed by '='
            next_tok = self._peek()
            if next_tok and next_tok.type == TOKEN_EQUALS:
                name_token = self._consume(TOKEN_IDENTIFIER)
                self._consume(TOKEN_EQUALS)
                value_node = self._parse_expression()
                return VarAssignNode(name_token.value, value_node)

        # ── print <expr> ────────────────────────────────────
        if token.type == "PRINT":
            self.pos += 1                                   # consume PRINT
            expr_node = self._parse_expression()
            return PrintNode(expr_node)

        # ── fallback: bare expression ────────────────────────
        return self._parse_expression()

    # ── public API ───────────────────────────────────────────

    def parse(self) -> list:
        """Parse all statements until EOF and return a list of
        AST nodes."""
        statements: list = []

        while self._current_token().type != TOKEN_EOF:
            statements.append(self._parse_statement())

        return statements


# ── Quick smoke test ─────────────────────────────────────────
if __name__ == "__main__":
    source = "let x = 10 + 5"
    print(f'Source : "{source}"\n')

    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    print("AST:")
    for node in ast:
        print(f"  {node}")
