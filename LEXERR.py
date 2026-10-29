import sys
from pathlib import Path

# ---------------------------------------------------------------
# Mini Java Lexical Analyzer (Phase 1)
# tokenize(source_code) can be imported and used by the Phase 2 parser.
# ---------------------------------------------------------------

KEYWORDS = {
    "class": "CLASS",
    "public": "PUBLIC",
    "static": "STATIC",
    "void": "VOID",
    "int": "INT",
    "float": "FLOAT",
    "boolean": "BOOLEAN_TYPE",
    "char": "CHAR",
    "String": "STRING_TYPE",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "return": "RETURN",
}

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
WHITESPACE = " \t\n\r"

OPERATORS = {
    "=": "ASSIGN",
    "+": "MATHOP",
    "-": "MATHOP",
    "*": "MATHOP",
    "/": "MATHOP",
    "%": "MATHOP",
    ">": "LOGOP",
    "<": "LOGOP",
    ">=": "LOGOP",
    "<=": "LOGOP",
    "==": "LOGOP",
    "!=": "LOGOP",
    "&&": "LOGOP",   # remove these 3 lines if they are not in the PDF table
    "||": "LOGOP",
    "!": "LOGOP",
}

PUNCTUATION = {
    "(": "LPAR",
    ")": "RPAR",
    "{": "LCUR",
    "}": "RCUR",
    "[": "LSQU",
    "]": "RSQU",
    ";": "SEMICOLON",
    ",": "COMMA",
    ".": "DOT",
}


def is_word_char(c):
    """True if c can appear inside an identifier (letter, digit, underscore)."""
    return c in LETTERS or c in DIGITS or c == "_"


def is_word_start(c):
    """True if c can start an identifier (letter or underscore)."""
    return c in LETTERS or c == "_"


def read_word(source, pos):
    """Return the index just after the run of word characters starting at pos."""
    j = pos
    while j < len(source) and is_word_char(source[j]):
        j += 1
    return j


def tokenize(source_code):
    """
    Scan source_code and return (tokens, errors, symbol_table).

    tokens       : list of (lexeme, token_type, line, column)
    errors       : list of error message strings
    symbol_table : dict  name -> {"line", "column", "count"}  (first occurrence)
    """
    tokens = []
    errors = []
    symbol_table = {}

    i = 0
    line = 1
    column = 1
    n = len(source_code)

    while i < n:
        char = source_code[i]

        # 1. Skip whitespace
        if char in WHITESPACE:
            if char == "\n":
                line += 1
                column = 1
            else:
                column += 1
            i += 1
            continue

        # 2. Skip comments
        if char == "/" and i + 1 < n:

            # Single-line comment
            if source_code[i + 1] == "/":
                i += 2
                column += 2
                while i < n and source_code[i] != "\n":
                    i += 1
                    column += 1
                continue

            # Multi-line comment
            if source_code[i + 1] == "*":
                comment_line = line
                comment_column = column
                i += 2
                column += 2
                closed = False

                while i < n:
                    if source_code[i] == "*" and i + 1 < n and source_code[i + 1] == "/":
                        i += 2
                        column += 2
                        closed = True
                        break
                    if source_code[i] == "\n":
                        line += 1
                        column = 1
                    else:
                        column += 1
                    i += 1

                if not closed:
                    errors.append(
                        "Error: unclosed comment starting at line "
                        + str(comment_line) + ", column " + str(comment_column) + "."
                    )
                continue

        # Remember where this token starts
        start_line = line
        start_column = column

        # 3. Numbers, and identifiers that start with a digit (invalid)
        if char in DIGITS:
            j = i
            while j < n and source_code[j] in DIGITS:
                j += 1

            # Digits followed directly by a letter or underscore -> invalid identifier
            if j < n and is_word_start(source_code[j]):
                j = read_word(source_code, j)
                lexeme = source_code[i:j]
                errors.append(
                    "Error: invalid identifier '" + lexeme + "' at line "
                    + str(start_line) + ", column " + str(start_column) + "."
                )
                column += j - i
                i = j
                continue

            # Fractional part (only if a digit follows the dot)
            if j + 1 < n and source_code[j] == "." and source_code[j + 1] in DIGITS:
                j += 1
                while j < n and source_code[j] in DIGITS:
                    j += 1

            lexeme = source_code[i:j]
            tokens.append((lexeme, "NUMBER", start_line, start_column))
            column += j - i
            i = j
            continue

        # 4. Identifiers, keywords, booleans
        if is_word_start(char):
            j = read_word(source_code, i)

            # Names like total-marks or student@id are invalid identifiers
            if (
                j + 1 < n
                and source_code[j] in "-@"
                and is_word_start(source_code[j + 1])
            ):
                k = read_word(source_code, j + 1)
                invalid_name = source_code[i:k]
                errors.append(
                    "Error: invalid identifier '" + invalid_name + "' at line "
                    + str(start_line) + ", column " + str(start_column) + "."
                )
                column += k - i
                i = k
                continue

            lexeme = source_code[i:j]

            if lexeme == "main":
                token_type = "MAIN"
            elif lexeme in KEYWORDS:
                token_type = KEYWORDS[lexeme]
            elif lexeme == "true" or lexeme == "false":
                token_type = "BOOLEAN"
            else:
                token_type = "IDENTIFIER"

            tokens.append((lexeme, token_type, start_line, start_column))

            if token_type == "IDENTIFIER":
                if lexeme in symbol_table:
                    symbol_table[lexeme]["count"] += 1
                else:
                    symbol_table[lexeme] = {
                        "line": start_line,
                        "column": start_column,
                        "count": 1,
                    }

            column += j - i
            i = j
            continue

        # 5. Strings and character literals
        if char == '"' or char == "'":
            quote = char
            string_start = i
            i += 1
            column += 1
            closed = False

            while i < n:
                current = source_code[i]

                # A string cannot continue onto the next line
                if current == "\n":
                    break

                # Escaped character such as \" or \'
                if current == "\\" and i + 1 < n and source_code[i + 1] != "\n":
                    i += 2
                    column += 2
                    continue

                if current == quote:
                    i += 1
                    column += 1
                    closed = True
                    break

                i += 1
                column += 1

            if closed:
                lexeme = source_code[string_start:i]
                tokens.append((lexeme, "STRING", start_line, start_column))
            else:
                errors.append(
                    "Error: unclosed string literal starting at line "
                    + str(start_line) + ", column " + str(start_column) + "."
                )
                # Skip the newline that ended the broken string
                if i < n and source_code[i] == "\n":
                    i += 1
                    line += 1
                    column = 1
            continue

        # 6. Operators (try two characters first, then one)
        matched = False
        for length in (2, 1):
            if i + length <= n:
                candidate = source_code[i:i + length]
                if candidate in OPERATORS:
                    tokens.append((candidate, OPERATORS[candidate], start_line, start_column))
                    i += length
                    column += length
                    matched = True
                    break
        if matched:
            continue

        # 7. Punctuation
        if char in PUNCTUATION:
            tokens.append((char, PUNCTUATION[char], start_line, start_column))
            i += 1
            column += 1
            continue

        # 8. Anything else is an invalid character
        errors.append(
            "Error: invalid character '" + char + "' at line "
            + str(start_line) + ", column " + str(start_column) + "."
        )
        i += 1
        column += 1

    return tokens, errors, symbol_table


def print_output(tokens, errors, symbol_table):
    """Console output in the same style as the PDF sample."""
    for lexeme, token_type, _, _ in tokens:
        print("Lexeme: " + lexeme + ", Token: " + token_type)

    print()
    print("Symbol Table:")
    for name, info in symbol_table.items():
        print("  " + name + " (first at line " + str(info["line"])
              + ", column " + str(info["column"])
              + ", used " + str(info["count"]) + " time(s))")

    print()
    if errors:
        for error in errors:
            print(error)
    else:
        print("No lexical errors found.")


# ---------------------------------------------------------------
# GUI
# ---------------------------------------------------------------
def show_results(tokens, errors, symbol_table):
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Mini Java | Lexical Analyzer")
    root.geometry("1100x720")
    root.minsize(850, 550)
    root.configure(bg="#101827")

    # ---------- COLORS ----------
    BG = "#101827"
    PANEL = "#1b263b"
    HEADER = "#243653"
    ACCENT = "#7c5cff"
    TEXT = "#f1f5f9"
    MUTED = "#a8b6cc"
    GREEN = "#34d399"
    RED = "#fb7185"

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=PANEL,
        foreground=TEXT,
        fieldbackground=PANEL,
        rowheight=34,
        font=("Consolas", 11),
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=HEADER,
        foreground="#ffffff",
        font=("Arial", 11, "bold"),
        padding=10,
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#ffffff")],
    )
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=PANEL,
        foreground=TEXT,
        padding=[18, 10],
        font=("Arial", 10, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#ffffff")],
    )

    # ---------- HEADER ----------
    tk.Label(
        root, text="MINI JAVA", font=("Arial", 12, "bold"), bg=BG, fg="#a78bfa"
    ).pack(anchor="w", padx=25, pady=(20, 0))

    tk.Label(
        root, text="Lexical Analyzer", font=("Arial", 26, "bold"), bg=BG, fg=TEXT
    ).pack(anchor="w", padx=25, pady=(3, 2))

    tk.Label(
        root,
        text="Tokens • Symbol Table • Lexical Errors",
        font=("Arial", 11),
        bg=BG,
        fg=MUTED,
    ).pack(anchor="w", padx=25, pady=(0, 18))

    # ---------- SUMMARY CARDS ----------
    cards = tk.Frame(root, bg=BG)
    cards.pack(fill="x", padx=25, pady=(0, 18))

    def make_card(parent, label, value, color):
        card = tk.Frame(parent, bg=PANEL, padx=18, pady=12)
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(card, text=label, bg=PANEL, fg=MUTED, font=("Arial", 10)).pack(anchor="w")
        tk.Label(
            card, text=str(value), bg=PANEL, fg=color, font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(4, 0))

    make_card(cards, "TOTAL TOKENS", len(tokens), "#a78bfa")
    make_card(cards, "IDENTIFIERS", len(symbol_table), GREEN)
    make_card(cards, "LEXICAL ERRORS", len(errors), RED)

    # ---------- SEARCH ----------
    search_frame = tk.Frame(root, bg=BG)
    search_frame.pack(fill="x", padx=25, pady=(0, 12))

    tk.Label(
        search_frame, text="Search tokens:", bg=BG, fg=TEXT, font=("Arial", 10, "bold")
    ).pack(side="left", padx=(0, 10))

    search_var = tk.StringVar()
    tk.Entry(
        search_frame,
        textvariable=search_var,
        bg=PANEL,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        font=("Arial", 11),
    ).pack(side="left", fill="x", expand=True, ipady=8)

    # ---------- NOTEBOOK ----------
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    # ----- Tab 1: Tokens -----
    token_frame = tk.Frame(notebook, bg=PANEL)
    notebook.add(token_frame, text="  Tokens  ")

    columns = ("No.", "Lexeme", "Token Type", "Category")
    table = ttk.Treeview(token_frame, columns=columns, show="headings")

    table.heading("No.", text="#")
    table.heading("Lexeme", text="Lexeme")
    table.heading("Token Type", text="Token Type")
    table.heading("Category", text="Category")

    table.column("No.", width=65, anchor="center")
    table.column("Lexeme", width=300, anchor="w")
    table.column("Token Type", width=230, anchor="center")
    table.column("Category", width=200, anchor="center")

    scrollbar = ttk.Scrollbar(token_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
    scrollbar.pack(side="right", fill="y", padx=(0, 12), pady=12)

    table.tag_configure("keyword", foreground="#c4b5fd")
    table.tag_configure("identifier", foreground="#6ee7b7")
    table.tag_configure("number", foreground="#fcd34d")
    table.tag_configure("string", foreground="#7dd3fc")
    table.tag_configure("operator", foreground="#f9a8d4")
    table.tag_configure("punctuation", foreground="#cbd5e1")
    table.tag_configure("other", foreground="#f1f5f9")

    def get_token_data(token):
        lexeme, token_type = token[0], token[1]

        if token_type == "IDENTIFIER":
            category, tag = "Identifier", "identifier"
        elif token_type in {"NUMBER", "STRING", "BOOLEAN"}:
            category = "Literal"
            tag = "number" if token_type == "NUMBER" else "string"
        elif token_type in {"ASSIGN", "LOGOP", "MATHOP"}:
            category, tag = "Operator", "operator"
        elif token_type in set(PUNCTUATION.values()):
            category, tag = "Punctuation", "punctuation"
        elif token_type == "MAIN" or token_type in set(KEYWORDS.values()):
            category, tag = "Keyword", "keyword"
        else:
            category, tag = "Other", "other"

        return lexeme, token_type, category, tag

    def populate_tokens(*args):
        query = search_var.get().lower().strip()

        for item in table.get_children():
            table.delete(item)

        for number, token in enumerate(tokens, start=1):
            lexeme, token_type, category, tag = get_token_data(token)

            if query and query not in (
                lexeme.lower() + " " + token_type.lower() + " " + category.lower()
            ):
                continue

            table.insert(
                "",
                "end",
                values=(number, lexeme, token_type, category),
                tags=(tag,),
            )

    search_var.trace_add("write", populate_tokens)
    populate_tokens()

    # ----- Tab 2: Symbol Table -----
    symbol_frame = tk.Frame(notebook, bg=PANEL)
    notebook.add(symbol_frame, text="  Symbol Table  ")

    symbol_columns = ("No.", "Name", "Line", "Column", "Occurrences")
    symbol_view = ttk.Treeview(symbol_frame, columns=symbol_columns, show="headings")

    symbol_view.heading("No.", text="#")
    symbol_view.heading("Name", text="Identifier")
    symbol_view.heading("Line", text="First Line")
    symbol_view.heading("Column", text="First Column")
    symbol_view.heading("Occurrences", text="Occurrences")

    symbol_view.column("No.", width=60, anchor="center")
    symbol_view.column("Name", width=350, anchor="w")
    symbol_view.column("Line", width=120, anchor="center")
    symbol_view.column("Column", width=120, anchor="center")
    symbol_view.column("Occurrences", width=140, anchor="center")

    symbol_view.pack(fill="both", expand=True, padx=12, pady=12)
    symbol_view.tag_configure("identifier", foreground="#6ee7b7")

    for number, (name, info) in enumerate(symbol_table.items(), start=1):
        symbol_view.insert(
            "",
            "end",
            values=(number, name, info["line"], info["column"], info["count"]),
            tags=("identifier",),
        )

    # ----- Tab 3: Errors -----
    error_frame = tk.Frame(notebook, bg=PANEL)
    notebook.add(error_frame, text="  Lexical Errors  ")

    error_table = ttk.Treeview(
        error_frame, columns=("No.", "Error Message"), show="headings"
    )
    error_table.heading("No.", text="#")
    error_table.heading("Error Message", text="Error Message")
    error_table.column("No.", width=65, anchor="center")
    error_table.column("Error Message", width=850, anchor="w")

    error_table.pack(fill="both", expand=True, padx=12, pady=12)
    error_table.tag_configure("error", foreground=RED)
    error_table.tag_configure("success", foreground=GREEN)

    if errors:
        for number, error in enumerate(errors, start=1):
            error_table.insert(
                "", "end", values=(number, str(error)), tags=("error",)
            )
    else:
        error_table.insert(
            "", "end", values=("-", "No lexical errors found."), tags=("success",)
        )

    root.mainloop()


if __name__ == "__main__":
    file_name = sys.argv[1] if len(sys.argv) > 1 else "Test Cases.txt"
    source_code = Path(file_name).read_text(encoding="utf-8")

    tokens, errors, symbol_table = tokenize(source_code)
    print_output(tokens, errors, symbol_table)
    show_results(tokens, errors, symbol_table)
