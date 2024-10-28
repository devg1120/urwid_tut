import pygments.lexers

# 直接lexerクラスのコンストラクタを使ってlexerのインスタンスを取得

lexer=pygments.lexers.PythonLexer();
print(type(lexer))

text = "def test():"
r = lexer.get_tokens_unprocessed(text);
for t in r:
    print(t)


file = "./new_edit.py"

f = open(file, mode="r")

lines = f.readlines()

token_dict = {}
c = 0
for line in lines:
    c += 1
    r = lexer.get_tokens_unprocessed(line);
    for t in r:
        print(str(c).zfill(3),t)
        if t[1] in token_dict :
            token_dict[t[1]] += 1
        else:
            token_dict[t[1]] = 1

for k in token_dict:
    print(k)

token_dict_sorted = sorted( token_dict.items())
for k in token_dict_sorted:
    #print(k)
    print(type(k[0]))



key_list = [
 (pygments.token.Token.Comment.Hashbang, 1)
,(pygments.token.Token.Comment.Single, 95)
,(pygments.token.Token.Error, 10)
,(pygments.token.Token.Keyword, 228)
,(pygments.token.Token.Keyword.Constant, 98)
,(pygments.token.Token.Keyword.Namespace, 11)
,(pygments.token.Token.Literal.Number.Integer, 57)
,(pygments.token.Token.Literal.String.Affix, 11)
,(pygments.token.Token.Literal.String.Doc, 10)
,(pygments.token.Token.Literal.String.Double, 423)
,(pygments.token.Token.Literal.String.Escape, 5)
,(pygments.token.Token.Literal.String.Interpol, 2)
,(pygments.token.Token.Literal.String.Single, 205)
,(pygments.token.Token.Name, 991)
,(pygments.token.Token.Name.Builtin, 73)
,(pygments.token.Token.Name.Builtin.Pseudo, 307)
,(pygments.token.Token.Name.Class, 4)
,(pygments.token.Token.Name.Exception, 2)
,(pygments.token.Token.Name.Function, 43)
,(pygments.token.Token.Name.Function.Magic, 7)
,(pygments.token.Token.Name.Namespace, 11)
,(pygments.token.Token.Name.Variable.Magic, 2)
,(pygments.token.Token.Operator, 861)
,(pygments.token.Token.Operator.Word, 24)
,(pygments.token.Token.Punctuation, 1111)
,(pygments.token.Token.Text, 2476)
]

for t in key_list:
    print(t)

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

print("------- dict")
for k in key_dict:
    print(k, key_dict[k][0], key_dict[k][1])

print("-------------")
c = 0
for line in lines:
    c += 1
    r = lexer.get_tokens_unprocessed(line);
    for t in r:
         print(t[1], end=" ")
         print(key_dict[t[1]], )

print("-------------")
r = lexer.get_tokens_unprocessed(text);
for t in r:
     print(t, end=" ")
     print(t[1], end=" ")
     print(key_dict[t[1]], )
