package src;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.List;

import src.Lexer;
import src.Parser;

public class Main {
    public static void main(String[] args) {
    Lexer lexer = new Lexer();
    String text = Main.readStdin();
    List<Lexer.Token> tokens = lexer.tokenize(text);
    //System.out.println(tokens);
    Parser parser = new Parser(tokens);
    String json = parser.parse().toJson();
    System.out.println(json);
  }

  private static String readStdin() {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    String content = "";
    try {
      String line = "";
      while ((line = br.readLine()) != null) content += line + "\n";
    }
    catch (Exception e) {
      System.err.println(e.toString());
      System.exit(1);
    }
    return content;
  }

}
