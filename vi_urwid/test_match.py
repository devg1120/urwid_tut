import re

def find_all_matches(pattern, string):
    pat = re.compile('(' + pattern + ')')
    pos = 0
    out = {}
    while (match := pat.search(string, pos)) is not None:
        s = match.start() 
        e = match.end() 
        pos = s + 1
        #out[str(s)]=  (match[1],s,e-s )
        out[s]=  (match[1],s,e-s,e )
    return out

def build_keyword_list( ptns, line):
    tr = None
    for ptn in ptns:
        r = find_all_matches(ptn, line)  
        if tr == None:
            tr = r
        else:
            tr = tr | r
    return sorted(tr.items())

def build_attr(s):
  attr = []
  token = []

  #print("start: " +str(s[0][0]))
  if s[0][0] > 0:
    attr.append(("",s[0][0]))
    token.append("_" * s[0][0])
    attr.append(("rect",s[0][1][2]))
    token.append(s[0][1][0])
    prev_end_next_pos= s[0][1][3]
    sti = 1
  else:
    prev_end_next_pos= 0
    sti = 0
  for e in s[sti:]:
    #print(e[0])
    if prev_end_next_pos < e[0]:
        l = e[0] - prev_end_next_pos
        attr.append(("",l))
        token.append("_" * l )

    attr.append(("rect",e[1][2]))
    prev_end_next_pos= e[1][3]
    token.append(e[1][0])
   
  x = len(line) - prev_end_next_pos
  if x > 0:
     attr.append(("", x ))
     token.append("_" * x )

  return (attr,token)

def make_attr( keywords, line):
    kl = build_keyword_list(keywords,line)
    #print(kl)
    attr, token = build_attr(kl)
    return attr, token
###################################
line = "12AB3456AB789A"  
#line = "AB3456AB789AB"  
keywords = ['AB','45']

attr, token = make_attr(keywords,line)

print(line, len(line))
print(attr)
print(token)

