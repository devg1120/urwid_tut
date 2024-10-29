import pygments
import pygments.lexers
from pygments.token import Keyword, Name, Comment, String, Error, \
             Number, Operator, Generic

key_dict = {
        Comment.Hashbang :      ( 0, "a" ),
        Comment.Single:         ( 2, "b" ),
        Error:                  ( 3, "c" ),
        Keyword:                ( 4, "d" ),
        Keyword.Constant:       ( 5, "e" ),
        Keyword.Namespace:      ( 6, "f" ),
        Literal.Number.Integer: ( 7, "g" ),
        Literal.String.Affix:   ( 8, "h" ),
        Literal.String.Doc:     ( 9, "i" ),
        Literal.String.Double:  (10, "j" ),
        Literal.String.Escape:  (11, "k" ),
        Literal.String.Interpol:(12, "l" ),
        Literal.String.Single:  (13, "m" ),
        Name:                   (14, "n" ),
        Name.Builtin:           (15, "o" ),
        Name.Builtin.Pseudo:    (16, "p" ),
        Name.Class:             (17, "q" ),
        Name.Exception:         (18, "r" ),
        Name.Function:          (19, "s" ),
        Name.Function.Magic:    (20, "t" ),
        Name.Namespace:         (21, "u" ),
        Name.Variable.Magic:    (22, "v" ),
        Operator:               (23, "w" ),
        Operator.Word:          (24, "x" ),
        Punctuation:            (25, "y" ),
        Text:                   (26, "z" ),
}

"""
key_dict = {
        pygments.token.Token.Comment.Hashbang :      ( 1, "a" ),
        pygments.token.Token.Comment.Single:         ( 2, "b" ),
        pygments.token.Token.Error:                  ( 3, "c" ),
        pygments.token.Token.Keyword:                ( 4, "d" ),
        pygments.token.Token.Keyword.Constant:       ( 5, "e" ),
        pygments.token.Token.Keyword.Namespace:      ( 6, "f" ),
        pygments.token.Token.Literal.Number.Integer: ( 7, "g" ),
        pygments.token.Token.Literal.String.Affix:   ( 8, "h" ),
        pygments.token.Token.Literal.String.Doc:     ( 9, "i" ),
        pygments.token.Token.Literal.String.Double:  (10, "j" ),
        pygments.token.Token.Literal.String.Escape:  (11, "k" ),
        pygments.token.Token.Literal.String.Interpol:(12, "l" ),
        pygments.token.Token.Literal.String.Single:  (13, "m" ),
        pygments.token.Token.Name:                   (14, "n" ),
        pygments.token.Token.Name.Builtin:           (15, "o" ),
        pygments.token.Token.Name.Builtin.Pseudo:    (16, "p" ),
        pygments.token.Token.Name.Class:             (17, "q" ),
        pygments.token.Token.Name.Exception:         (18, "r" ),
        pygments.token.Token.Name.Function:          (19, "s" ),
        pygments.token.Token.Name.Function.Magic:    (20, "t" ),
        pygments.token.Token.Name.Namespace:         (21, "u" ),
        pygments.token.Token.Name.Variable.Magic:    (22, "v" ),
        pygments.token.Token.Operator:               (23, "w" ),
        pygments.token.Token.Operator.Word:          (24, "x" ),
        pygments.token.Token.Punctuation:            (25, "y" ),
        pygments.token.Token.Text:                   (26, "z" ),
}
"""

#print("------- dict")
#for k in key_dict:
#    print(k, key_dict[k][0], key_dict[k][1])


lexer=pygments.lexers.PythonLexer();
print(type(lexer))

print("-------------")

text = "def test():"

r = lexer.get_tokens_unprocessed(text);
for t in r:
     print(t, end=" ")
     print(t[1], end=" ")
     print(key_dict[t[1]] )
     #print(key_dict[t[1]],key_dict[t[1]][0] )
