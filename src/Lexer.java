package src;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;
import java.util.function.Predicate;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
public class Lexer {


  // private static final List<Pair<String, Pattern>> REGEXS =
  //   List.of(new Pair<>("IGNORE", Pattern.compile("(?:[ \\t]+|\\#.*)+")),
  //           new Pair<>("INT", Pattern.compile("\\d+")),
  //           new Pair<>("CHAR", Pattern.compile(".|\\n")));

  private static final List<Pair<String, Pattern>> REGEXS = initializeRegexs();

  private static List<Pair<String, Pattern>> initializeRegexs() {
      List<Pair<String, Pattern>> regexs = new ArrayList<>();
      regexs.add(new Pair<>("IGNORE", Pattern.compile("(?:[ \\t]+|\\#.*)+")));
      regexs.add(new Pair<>("INT", Pattern.compile("\\d+")));
      regexs.add(new Pair<>("CHAR", Pattern.compile(".|\\n")));
      return regexs;
  }

  private static Pair<String, Matcher> nextMatch(String text) {
    for (Pair<String, Pattern> pair : REGEXS) {
      Matcher m = pair.val2.matcher(text);
      if (m.lookingAt()) 
        return new Pair<>(pair.val1, m);
    }
    return null;
  }

  List<Token> tokenize(String text) {
    List<Token> tokens = new ArrayList<>();
    while (text.length() > 0) {
      Pair<String, Matcher> pair = nextMatch(text);
      String kind = pair.val1;
      Matcher matcher = pair.val2;
      String lexeme = text.substring(0, matcher.end());
      switch (kind) {
      case "IGNORE":
        break;
      default:
        tokens.add(new Token("CHAR".equals(kind) ? lexeme : kind, lexeme));
        break;
      }
      text = text.substring(lexeme.length());
    }
    tokens.add(new Token("<EOF>", "<EOF>"));
    return tokens;
  }

  static class Token {
    final String kind;
    final String lexeme;

    Token(String kind, String lexeme) {
      this.kind = kind; this.lexeme = lexeme;
    }
    public String toString() {
      return String.format("{kind:\"%s\", lexeme:\"%s\"}",
                           this.kind, this.lexeme);
    }
  }

  static class Pair<T1, T2> {
    final T1 val1;
    final T2 val2;
    Pair(T1 v1, T2 v2) { val1 = v1; val2 = v2; }
  }

}