package src;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.stream.Collectors;


import src.Lexer.Token;

/*
program:
  : '\n'+ program
  | #empty
  | expr program
  ;
expr
  : term ( ( '+' | '-' )  term )*
  ;
term
  : factor ( ( '*' | '/' ) factor )*
  ;
factor
  : '-' factor
  |  INTEGER
  |  '(' expr ')'
  ;
*/
class Parser {
  private final List<Token> tokens;
  private Token tok;
  private int nextIndex;

  Parser(List<Token> tokens) {
    this.tokens = tokens;
    this.nextIndex = 0;
    this.tok = nextToken();
  }

  //wrapper used for crude  error recovery
  Ast parse() {
    List asts = new ArrayList<Ast>();
    this.program(asts);
    if (!peek("<EOF>")) {
      die("expecting end-of-file at '" + tok.lexeme + "`");
    }
    return new ListAst(asts);
  }

  private List<Ast> program(List<Ast> asts) {
    if (peek("\n")) {
      while (peek("\n")) consume("\n");
      return program(asts);
    }
    else if (peek("<EOF>")) {
      return asts;
    }
    else {
      final var e = expr();
      asts.add(e);
      return program(asts);
    }
  }

  private Ast expr() {
    var t = term();
    while (peek("+") || peek("-")) {
      var op = tok.kind;
      consume(op);
      var t1 = term();
      var kids = new ArrayList<Ast>();
      kids.add(t); kids.add(t1);
      t = new OpAst(op, kids);
    }
    return t;
  }

  private Ast term() {
    var f = factor();
    while (peek("*") || peek("/")) {
      var op = tok.kind;
      consume(op);
      var f1 = factor();
      var kids = new ArrayList<Ast>();
      kids.add(f); kids.add(f1);
      f = new OpAst(op, kids);
    }
    return f;
  }

  private Ast factor() {
    if (peek("-")) {
      consume("-");
      var f = factor();
      var kids = new ArrayList<Ast>();
      kids.add(f);
      f = new OpAst("-", kids);
      return f;
    }
    else if (peek("INT")) {
      var val = Integer.valueOf(tok.lexeme);
      consume("INT");
      return new IntAst(val);
    }
    else {
      consume("(");
      var e = expr();
      consume(")");
      return e;
    }
  }

  private Token nextToken() {
    return tokens.get(nextIndex++);
  }

  private boolean peek(String kind) {
    return tok.kind.equals(kind);
  }

  private void consume(String kind) {
    if (peek(kind)) {
      tok = nextToken();
    }
    else {
      String msg = String.format("syntax error: expecting '%s' at '%s'",
                                 kind, tok.lexeme);
      die(msg);
    }
  }

  private void die(String msg) {
    System.err.println(msg);
    System.exit(1);
  }

  static abstract class Ast {
    abstract String toJson();
  };

  private static class ListAst extends Ast {
    private final List<Ast> kids;
    ListAst(List<Ast> kids) {
      this.kids = kids;
    }
    String toJson() {
      return "["
        + this.kids.stream()
          .map(Ast::toJson)
          .collect(Collectors.joining(","))
        + "]";
    }
  }

  private static class OpAst extends Ast {
    private final String tag;
    private final List<Ast> kids;
    OpAst(String tag, List<Ast> kids) {
      this.tag = tag; this.kids = kids;
    }
    String toJson() {
      return "{\"tag\":\"" + this.tag + "\",\"kids\":["
        + this.kids.stream()
          .map(Ast::toJson)
          .collect(Collectors.joining(","))
        + "]}";
    }
  }

  private static class IntAst extends Ast {
    private final int val;
    IntAst(int val) { this.val = val; }
    String toJson() {
      return String.valueOf(val);
    }
  }




}
