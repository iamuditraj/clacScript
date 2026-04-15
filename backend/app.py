# ============================================================
# CalcScript API — Flask server exposing the compiler pipeline
# ============================================================

import io
import contextlib

from flask import Flask, request, jsonify
from flask_cors import CORS

from lexer import Lexer
from parser import Parser
from evaluator import Evaluator

# ── Flask setup ──────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # allow cross-origin requests from the frontend


# ── POST /api/run ────────────────────────────────────────────
@app.route("/api/run", methods=["POST"])
def run_code():
    """Accept CalcScript source code, execute it through the
    Lexer → Parser → Evaluator pipeline, and return the
    captured stdout (or an error message) as JSON.

    Request body
    ------------
    {
        "code": "let x = 10 + 5\\nprint x"
    }

    Success response
    ----------------
    {
        "success": true,
        "output": "15\\n"
    }

    Error response
    --------------
    {
        "success": false,
        "error": "CalcScript Runtime Error: ..."
    }
    """
    data = request.get_json(silent=True)

    if not data or "code" not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'code' field in request body.",
        }), 400

    source = data["code"]

    try:
        # 1. Lex
        tokens = Lexer(source).tokenize()

        # 2. Parse
        ast = Parser(tokens).parse()

        # 3. Evaluate — capture all print() output
        buffer = io.StringIO()
        evaluator = Evaluator()

        with contextlib.redirect_stdout(buffer):
            evaluator.run(ast)

        output = buffer.getvalue()

        return jsonify({
            "success": True,
            "output": output,
        })

    except (SyntaxError, NameError, ZeroDivisionError, RuntimeError) as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    except Exception as exc:
        # Catch-all for anything unexpected
        return jsonify({
            "success": False,
            "error": f"Internal error: {exc}",
        }), 500


# ── Entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    print("CalcScript API running on http://localhost:5000")
    app.run(debug=True, port=5000)
