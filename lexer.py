from pathlib import Path
import tkinter as tk
from tkinter import ttk
# Read source code
source_code = Path("input.txt").read_text(encoding="utf-8")

keywords = {
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

letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits = "0123456789"
whitespace = " \t\n\r"

operators = {
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
}

punctuation = {
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

tokens = []
errors = []
symbol_table = []

i = 0
line = 1
column = 1
source_length = len(source_code)

while i < source_length:
    char = source_code[i]

    # 1. Skip whitespace
    if char in whitespace:
        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1

        i += 1
        continue

    # 2. Skip comments
    if char == "/" and i + 1 < source_length:

        # Single-line comment
        if source_code[i + 1] == "/":
            i += 2
            column += 2

            while i < source_length and source_code[i] != "\n":
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

            while i < source_length:
                if (
                    source_code[i] == "*"
                    and i + 1 < source_length
                    and source_code[i + 1] == "/"
                ):
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
                    "Unclosed comment at line "
                    + str(comment_line)
                    + ", column "
                    + str(comment_column)
                )

            continue

    # Save token starting position
    start = i
    start_line = line
    start_column = column

    # 3. Detect identifiers starting with a digit
    if char in digits:
        j = i

        while j < source_length:
            current = source_code[j]

            if (
                current in letters
                or current in digits
                or current == "_"
            ):
                j += 1
            else:
                break

        if j > i and (
            source_code[j - 1] in letters
            or source_code[j - 1] == "_"
        ):
            lexeme = source_code[i:j]

            errors.append(
                "Invalid identifier '"
                + lexeme
                + "' at line "
                + str(start_line)
                + ", column "
                + str(start_column)
            )

            while i < j:
                i += 1
                column += 1

            continue

    # 4. Recognize identifiers and keywords
    if char in letters or char == "_":
        while i < source_length:
            current = source_code[i]

            if (
                current in letters
                or current in digits
                or current == "_"
            ):
                i += 1
                column += 1
            else:
                break

        lexeme = source_code[start:i]

        # Detect names containing an adjacent hyphen,
        # such as total-marks, as required by the assignment.
        if (
            i < source_length
            and source_code[i] == "-"
            and i + 1 < source_length
            and (
                source_code[i + 1] in letters
                or source_code[i + 1] == "_"
            )
        ):
            j = i + 1

            while j < source_length:
                current = source_code[j]

                if (
                    current in letters
                    or current in digits
                    or current == "_"
                ):
                    j += 1
                else:
                    break

            invalid_name = source_code[start:j]

            errors.append(
                "Invalid identifier '"
                + invalid_name
                + "' at line "
                + str(start_line)
                + ", column "
                + str(start_column)
            )

            column += j - i
            i = j
            continue

        # Detect names containing @, such as student@id
        if (
            i < source_length
            and source_code[i] == "@"
            and i + 1 < source_length
            and (
                source_code[i + 1] in letters
                or source_code[i + 1] == "_"
            )
        ):
            j = i + 1

            while j < source_length:
                current = source_code[j]

                if (
                    current in letters
                    or current in digits
                    or current == "_"
                ):
                    j += 1
                else:
                    break

            invalid_name = source_code[start:j]

            errors.append(
                "Invalid identifier '"
                + invalid_name
                + "' at line "
                + str(start_line)
                + ", column "
                + str(start_column)
            )

            column += j - i
            i = j
            continue

        token_type = "IDENTIFIER"

        if lexeme == "main":
            token_type = "MAIN"
        elif lexeme in keywords:
            token_type = keywords[lexeme]
        elif lexeme == "true" or lexeme == "false":
            token_type = "BOOLEAN"

        tokens.append((lexeme, token_type))

        if token_type == "IDENTIFIER":
            if lexeme not in symbol_table:
                symbol_table.append(lexeme)

        continue

    # 5. Recognize numbers
    if char in digits:
        while i < source_length and source_code[i] in digits:
            i += 1
            column += 1

        if (
            i < source_length
            and source_code[i] == "."
            and i + 1 < source_length
            and source_code[i + 1] in digits
        ):
            i += 1
            column += 1

            while i < source_length and source_code[i] in digits:
                i += 1
                column += 1

        lexeme = source_code[start:i]
        tokens.append((lexeme, "NUMBER"))
        continue

    # 6. Recognize strings and character literals
    if char == '"' or char == "'":
        quote = char

        i += 1
        column += 1
        closed = False

        while i < source_length:
            current = source_code[i]

            # Stop if the string reaches a newline
            if current == "\n":
                break

            # Handle escaped characters, such as \" or \'
            if current == "\\":
                if i + 1 < source_length and source_code[i + 1] != "\n":
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
            lexeme = source_code[start:i]
            tokens.append((lexeme, "STRING"))
        else:
            errors.append(
                "Unclosed string at line "
                + str(start_line)
                + ", column "
                + str(start_column)
            )

            # Skip the rest of the invalid string line
            if i < source_length and source_code[i] == "\n":
                i += 1
                line += 1
                column = 1

        continue

    # 7. Recognize operators (two characters before one)
    matched = False

    for length in (2, 1):
        if i + length <= source_length:
            candidate = source_code[i:i + length]

            if candidate in operators:
                tokens.append((candidate, operators[candidate]))
                i += length
                column += length
                matched = True
                break

    if matched:
        continue

    # 8. Recognize punctuation
    if char in punctuation:
        tokens.append((char, punctuation[char]))
        i += 1
        column += 1
        continue

    # 9. Report unknown characters
    errors.append(
        "Invalid character '"
        + char
        + "' at line "
        + str(line)
        + ", column "
        + str(column)
    )

    i += 1
    column += 1

## UI + TABLE
def show_results():
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
        background="#1b263b",
        foreground=TEXT,
        fieldbackground="#1b263b",
        rowheight=34,
        font=("Consolas", 11),
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=HEADER,
        foreground="#ffffff",
        font=("Arial", 11, "bold"),
        padding=10
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#ffffff")]
    )
    style.configure(
        "TNotebook",
        background=BG,
        borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        background=PANEL,
        foreground=TEXT,
        padding=[18, 10],
        font=("Arial", 10, "bold")
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#ffffff")]
    )

    # ---------- HEADER ----------
    tk.Label(
        root,
        text="MINI JAVA",
        font=("Arial", 12, "bold"),
        bg=BG,
        fg="#a78bfa"
    ).pack(anchor="w", padx=25, pady=(20, 0))

    tk.Label(
        root,
        text="Lexical Analyzer",
        font=("Arial", 26, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(anchor="w", padx=25, pady=(3, 2))

    tk.Label(
        root,
        text="Tokens • Identifiers • Lexical Errors",
        font=("Arial", 11),
        bg=BG,
        fg=MUTED
    ).pack(anchor="w", padx=25, pady=(0, 18))

    # ---------- SUMMARY CARDS ----------
    cards = tk.Frame(root, bg=BG)
    cards.pack(fill="x", padx=25, pady=(0, 18))

    def make_card(parent, label, value, color):
        card = tk.Frame(parent, bg=PANEL, padx=18, pady=12)
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Label(
            card, text=label, bg=PANEL, fg=MUTED,
            font=("Arial", 10)
        ).pack(anchor="w")

        tk.Label(
            card, text=str(value), bg=PANEL, fg=color,
            font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(4, 0))

    make_card(cards, "TOTAL TOKENS", len(tokens), "#a78bfa")
    make_card(cards, "IDENTIFIERS", len(symbol_table), GREEN)
    make_card(cards, "LEXICAL ERRORS", len(errors), RED)

    # ---------- SEARCH ----------
    search_frame = tk.Frame(root, bg=BG)
    search_frame.pack(fill="x", padx=25, pady=(0, 12))

    tk.Label(
        search_frame, text="Search tokens:",
        bg=BG, fg=TEXT, font=("Arial", 10, "bold")
    ).pack(side="left", padx=(0, 10))

    search_var = tk.StringVar()
    search_entry = tk.Entry(
        search_frame,
        textvariable=search_var,
        bg=PANEL,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        font=("Arial", 11)
    )
    search_entry.pack(side="left", fill="x", expand=True, ipady=8)

    # ---------- NOTEBOOK ----------
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    # Main tab: tokens AND identifiers in the same table
    token_frame = tk.Frame(notebook, bg=PANEL)
    notebook.add(token_frame, text="  Tokens & Identifiers  ")

    columns = ("No.", "Lexeme", "Token Type", "Category")
    table = ttk.Treeview(
        token_frame,
        columns=columns,
        show="headings"
    )

    table.heading("No.", text="#")
    table.heading("Lexeme", text="Lexeme")
    table.heading("Token Type", text="Token Type")
    table.heading("Category", text="Category")

    table.column("No.", width=65, anchor="center")
    table.column("Lexeme", width=300, anchor="w")
    table.column("Token Type", width=230, anchor="center")
    table.column("Category", width=200, anchor="center")

    scrollbar = ttk.Scrollbar(
        token_frame, orient="vertical", command=table.yview
    )
    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
    scrollbar.pack(side="right", fill="y", padx=(0, 12), pady=12)

    # Color-coded rows
    table.tag_configure("keyword", foreground="#c4b5fd")
    table.tag_configure("identifier", foreground="#6ee7b7")
    table.tag_configure("number", foreground="#fcd34d")
    table.tag_configure("string", foreground="#7dd3fc")
    table.tag_configure("operator", foreground="#f9a8d4")
    table.tag_configure("punctuation", foreground="#cbd5e1")
    table.tag_configure("other", foreground="#f1f5f9")

    def get_token_data(token):
        if isinstance(token, dict):
            lexeme = token.get("lexeme", "")
            token_type = token.get("token", token.get("type", ""))
        else:
            lexeme, token_type = token[0], token[1]

        token_type = str(token_type)
        lexeme = str(lexeme)

        if token_type == "IDENTIFIER":
            category = "Identifier"
            tag = "identifier"
        elif token_type in {
            "NUMBER", "STRING", "BOOLEAN"
        }:
            category = "Literal"
            tag = "number" if token_type == "NUMBER" else "string"
        elif token_type in {
            "ASSIGN", "LOGOP", "MATHOP"
        }:
            category = "Operator"
            tag = "operator"
        elif token_type in {
            "LPAR", "RPAR", "LCUR", "RCUR",
            "LSQU", "RSQU", "SEMICOLON", "COMMA", "DOT"
        }:
            category = "Punctuation"
            tag = "punctuation"
        elif token_type in {
            "CLASS", "PUBLIC", "STATIC", "VOID", "MAIN",
            "INT", "FLOAT", "BOOLEAN_TYPE", "CHAR",
            "STRING_TYPE", "IF", "ELSE", "WHILE",
            "FOR", "RETURN"
        }:
            category = "Keyword"
            tag = "keyword"
        else:
            category = "Other"
            tag = "other"

        return lexeme, token_type, category, tag

    def populate_tokens(*args):
        query = search_var.get().lower().strip()

        for item in table.get_children():
            table.delete(item)

        for number, token in enumerate(tokens, start=1):
            lexeme, token_type, category, tag = get_token_data(token)

            if query and query not in (
                lexeme.lower() + " " +
                token_type.lower() + " " +
                category.lower()
            ):
                continue

            table.insert(
                "",
                "end",
                values=(number, lexeme, token_type, category),
                tags=(tag,)
            )

    search_var.trace_add("write", populate_tokens)
    populate_tokens()

    # Errors tab
    error_frame = tk.Frame(notebook, bg=PANEL)
    notebook.add(error_frame, text="  Lexical Errors  ")

    error_columns = ("No.", "Error Message")
    error_table = ttk.Treeview(
        error_frame,
        columns=error_columns,
        show="headings"
    )
    error_table.heading("No.", text="#")
    error_table.heading("Error Message", text="Error Message")
    error_table.column("No.", width=65, anchor="center")
    error_table.column("Error Message", width=850, anchor="w")

    error_table.pack(fill="both", expand=True, padx=12, pady=12)
    error_table.tag_configure("error", foreground="#fb7185")
    error_table.tag_configure("success", foreground="#34d399")

    if errors:
        for number, error in enumerate(errors, start=1):
            error_table.insert(
                "", "end",
                values=(number, str(error)),
                tags=("error",)
            )
    else:
        error_table.insert(
            "", "end",
            values=("-", "No lexical errors found."),
            tags=("success",)
        )

    root.mainloop()


show_results()
