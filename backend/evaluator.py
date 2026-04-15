# ============================================================
# CalcScript Evaluator — Tree-walking interpreter
# ============================================================

from lexer import Lexer, TOKEN_PLUS, TOKEN_MINUS, TOKEN_MUL, TOKEN_DIV
from parser import (
    Parser,
    NumberNode,
    VarAccessNode,
    VarInitNode,
    VarAssignNode,
    BinOpNode,
    PrintNode,
)


class Evaluator:
    """Walks the AST produced by the Parser and executes each
    node, maintaining variable state in a local symbol table.

    Usage
    -----
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        Evaluator().run(ast)
    """

    def __init__(self):
        self.symbol_table: dict[str, int | float] = {}

    # ── public API ───────────────────────────────────────────

    def run(self, statements: list) -> None:
        """Execute a list of AST statement nodes sequentially."""
        for stmt in statements:
            self.visit(stmt)

    # ── visitor dispatch ─────────────────────────────────────

    def visit(self, node):
        """Recursively evaluate *node* by dispatching to the
        appropriate ``_visit_<NodeType>`` method.

        Returns the computed value for expression nodes so that
        parent nodes can use it (e.g. BinOpNode needs left/right
        values).
        """
        method_name = f"_visit_{type(node).__name__}"
        visitor = getattr(self, method_name, None)

        if visitor is None:
            raise RuntimeError(
                f"CalcScript Runtime Error: no visitor for {type(node).__name__}"
            )

        return visitor(node)

    # ── node visitors ────────────────────────────────────────

    def _visit_NumberNode(self, node: NumberNode):
        """Return the raw numeric value."""
        return node.value

    def _visit_VarAccessNode(self, node: VarAccessNode):
        """Look up a variable in the symbol table."""
        name = node.name
        if name not in self.symbol_table:
            raise NameError(
                f"CalcScript Runtime Error: variable '{name}' is not defined"
            )
        return self.symbol_table[name]

    def _visit_VarInitNode(self, node: VarInitNode):
        """Initialise a new variable via ``let``."""
        name = node.name
        if name in self.symbol_table:
            raise NameError(
                f"CalcScript Runtime Error: variable '{name}' is already "
                f"declared — use assignment (without 'let') to update it"
            )
        value = self.visit(node.value_node)
        self.symbol_table[name] = value
        return value

    def _visit_VarAssignNode(self, node: VarAssignNode):
        """Re-assign an *existing* variable.  Throws if the
        variable was never declared with ``let``."""
        name = node.name
        if name not in self.symbol_table:
            raise NameError(
                f"CalcScript Runtime Error: cannot assign to '{name}' — "
                f"variable has not been declared (use 'let {name} = ...')"
            )
        value = self.visit(node.value_node)
        self.symbol_table[name] = value
        return value

    def _visit_BinOpNode(self, node: BinOpNode):
        """Evaluate a binary arithmetic operation."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = node.op.type

        if op_type == TOKEN_PLUS:
            return left + right
        if op_type == TOKEN_MINUS:
            return left - right
        if op_type == TOKEN_MUL:
            return left * right
        if op_type == TOKEN_DIV:
            if right == 0:
                raise ZeroDivisionError(
                    "CalcScript Runtime Error: division by zero"
                )
            return left / right

        raise RuntimeError(
            f"CalcScript Runtime Error: unknown operator '{node.op.value}'"
        )

    def _visit_PrintNode(self, node: PrintNode):
        """Evaluate the inner expression and print its result."""
        value = self.visit(node.expr_node)
        print(value)
        return value


# ── Quick smoke test ─────────────────────────────────────────
if __name__ == "__main__":
    source = "\n".join([
        "let x = 10 + 5",
        "let y = x * 2",
        "print y",
        "y = y + 1",
        "print y",
    ])

    print(f"Source:\n{source}\n")
    print("Output:")

    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    Evaluator().run(ast)
