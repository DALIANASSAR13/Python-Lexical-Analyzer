# Python Lexical Analyzer

## 1. Introduction
The aim of this project is to develop a lexical analyzer for Mini Java using Python. The program reads source code and divides it into tokens. It also creates a symbol table and detects lexical errors.

## 2. Tokens Recognized
The program recognizes the following token types:

- **Keywords:** `class`, `public`, `static`, `void`, `int`, `float`, `boolean`, `char`, `String`, `if`, `else`, `while`, `for`, and `return`.
- **Identifiers:** Names of variables and classes.
- **Numbers:** Integer and floating-point numbers.
- **Strings:** Text inside single or double quotes.
- **Boolean values:** `true` and `false`.
- **Operators:** Arithmetic operators and comparison operators.
- **Punctuation:** Parentheses, braces, brackets, commas, semicolons, and dots.

The program ignores whitespace and comments.

## 3. Symbol Table
The symbol table stores unique identifiers found in the source code. It records the first line and column where each identifier appears and how many times it is used.

## 4. Error Handling
The program detects invalid identifiers, invalid characters, unclosed strings, and unclosed multiline comments. It reports the line and column of each error.

## 5. User Interface
The project uses Tkinter to display the results in a graphical interface. It includes a token table, a symbol table, a lexical errors table, and a search feature. Different colors are used to make token categories easier to identify.

## 6. Challenges and Solutions
One challenge was recognizing multi-character operators such as `>=` and `==`. This was solved by checking two-character operators before single-character operators. Another challenge was tracking line and column positions, which helps report errors accurately.

## 7. Conclusion
This project helped me understand how lexical analysis works and how source code is divided into tokens. It also provides a foundation for connecting the lexer to the next phase of the compiler.
