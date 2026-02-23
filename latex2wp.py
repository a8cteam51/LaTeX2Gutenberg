"""
 Copyright 2009 Luca Trevisan

 This file is part of LaTeX2WP, a program that converts
 a LaTeX document into a format that is ready to be
 copied and pasted into WordPress.

 You are free to redistribute and/or modify LaTeX2WP under the
 terms of the GNU General Public License (GPL), version 3
 or (at your option) any later version.

 I hope you will find LaTeX2WP useful, but be advised that
 it comes WITHOUT ANY WARRANTY; without even the implied warranty
 of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GPL for more details.

 You should have received a copy of the GNU General Public
 License along with LaTeX2WP.  If you can't find it,
 see <http://www.gnu.org/licenses/>.
"""

import re
import json
from sys import argv
import latex2mathml.converter

from latex2wpstyle import *


ref={}

endlatex = "&fg="+textcolor
if HTML : endproof = "<img src='http://l.wordpress.com/latex.php?latex=\Box&fg=000000'>"


count = []
for i in range(maxcounter+1) : count = count + [0]
inthm = ""

esc = [["\\$","__dollar__"],
       ["\\%","__percent__"],
       ["\\&","__amp__"]]

M = M + [ ["\\it ","\\em "],
          ["\\emph{","{\\em "],
          ["\\more","<!-- wp:more -->\n<!--more-->\n<!-- /wp:more -->"],
          ["\\$","&#36;"],
          ["\\%","&#37;"],
          ["\\&","&amp;"],
          ["\\`a","&agrave;"],
          ["\\'a","&aacute;"],
          ["\\\"a","&auml;"],
          ["\\aa ","&aring;"],
          ["\\`e","&egrave;"],
          ["\\'e","&eacute;"],
          ["\\\"e","&euml;"],
          ["\\`i","&igrave;"],
          ["\\'i","&iacute;"],
          ["\\\"i","&iuml;"],
          ["\\`o","&ograve;"],
          ["\\'o","&oacute;"],
          ["\\\"o","&ouml;"],
          ["\\`o","&ograve;"],
          ["\\'o","&oacute;"],
          ["\\\"o","&ouml;"],
          ["\\H o","ő"],
          ["\\`u","&ugrave;"],
          ["\\'u","&uacute;"],
          ["\\\"u","&uuml;"],
          ["\\`u","&ugrave;"],
          ["\\'u","&uacute;"],
          ["\\\"u","&uuml;"] ]


cb = re.compile("\\{|}")

def extractbody(m) :

    begin = re.compile("\\\\begin\s*")
    m= begin.sub("\\\\begin",m)
    end = re.compile("\\\\end\s*")
    m = end.sub("\\\\end",m)
    
    beginenddoc = re.compile("\\\\begin\\{document}"
                          "|\\\\end\\{document}")
    parse = beginenddoc.split(m)
    if len(parse)== 1 :
       m = parse[0]
    else :
       m = parse[1]

    """
      removes comments, replaces double returns with <p> and
      other returns and multiple spaces by a single space.
    """

    for e in esc :
        m = m.replace(e[0],e[1])

    comments = re.compile("%.*?\n")
    m=comments.sub(" ",m)

        

    multiplereturns = re.compile("\n\n+")
    m= multiplereturns.sub ("__PARA__",m)
    spaces=re.compile("(\n|[ ])+")
    m=spaces.sub(" ",m)

    ifcommands = re.compile("\\\\iffalse|\\\\ifblog|\\\\iftex|\\\\fi")
    L=ifcommands.split(m)
    I=ifcommands.findall(m)
    m= L[0]
    for i in range(1,(len(L)+1)//2) :
        if (I[2*i-2]=="\\ifblog") :
            m=m+L[2*i-1]
        m=m+L[2*i]

    doubledollar = re.compile("\\$\\$")
    L=doubledollar.split(m)
    m=L[0]
    for i in range(1,(len(L)+1)//2) :
        m = m+ "\\[" + L[2*i-1] + "\\]" + L[2*i]

    return m


def converttables(m) :
        

    retable = re.compile("\\\\begin\s*\\{tabular}.*?\\\\end\s*\\{tabular}"
                         "|\\\\begin\s*\\{btabular}.*?\\\\end\s*\\{btabular}")
    tables = retable.findall(m)
    rest = retable.split(m)


    m = rest[0]
    for i in range(len(tables)) :
        if tables[i].find("{btabular}") != -1 :
            m = m + convertonetable(tables[i],True)
        else :
            m = m + convertonetable(tables[i],False)
        m = m + rest[i+1]


    return m


def convertmacros(m) :

    for i in range( len (M)  ) :
        m = m.replace(M[i][0],M[i][1])
    m=m.replace("\emph","\em")
    return (m)


def convertonetable(m,border) :

    tokens = re.compile("\\\\begin\\{tabular}\s*\\{.*?}"
                        "|\\\\end\\{tabular}"
                        "|\\\\begin\\{btabular}\s*\\{.*?}"
                        "|\\\\end\\{btabular}"
                        "|&|\\\\\\\\")

    align = { "c" : "center", "l" : "left" , "r" : "right" }

    T = tokens.findall(m)
    C = tokens.split(m)


    L = cb.split(T[0])
    format = L[3]

    columns = len(format)
    if border :
        m = "<!-- wp:table -->\n<figure class=\"wp-block-table\"><table><tbody><tr>"
    else :
        m="<!-- wp:table -->\n<figure class=\"wp-block-table\"><table><tbody><tr>"
    p=1
    i=0

    
    while T[p-1] != "\\end{tabular}" and T[p-1] != "\\end{btabular}":
        m = m + "<td align="+align[format[i]]+">" + C[p] + "</td>"
        p=p+1
        i=i+1
        if T[p-1]=="\\\\" :
            for i in range (p,columns) :
                m=m+"<td></td>"
            m=m+"</tr><tr>"
            i=0
    m = m+ "</tr></tbody></table></figure>\n<!-- /wp:table -->"
    return (m)
 



            
        
    

def separatemath(m) :
    mathre = re.compile("\\$.*?\\$"
                   "|\\\\begin\\{equation}.*?\\\\end\\{equation}"
                   "|\\\\\\[.*?\\\\\\]")
    math = mathre.findall(m)
    text = mathre.split(m)
    return(math,text)


def processmath( M ) :
    R = []
    counteq=0
    global ref

    mathdelim = re.compile("\\$"
                           "|\\\\begin\\{equation}"
                           "|\\\\end\\{equation}"
                           "|\\\\\\[|\\\\\\]")
    label = re.compile("\\\\label\\{.*?}")
    
    for m in M :
        md = mathdelim.findall(m)
        mb = mathdelim.split(m)

        """
          In what follows, md[0] contains the initial delimiter,
          which is either \begin{equation}, or $, or \[, and
          mb[1] contains the actual mathematical equation
        """
        
        if md[0] == "$" :
            if HTML :
                m=m.replace("$","") 
                m=m.replace("+","%2B") 
                m=m.replace(" ","+")
                m=m.replace("'","&#39;")
                m="<img src='http://l.wordpress.com/latex.php?latex=%7B"+m+"%7D"+endlatex+"'>"
            else :
                m=_make_inline_math("{"+mb[1]+"}")

        else :
            if md[0].find("\\begin") != -1 :
                count[T["equation"]] = count[T["equation"]] + 1
                mb[1] = mb[1] + "\\ \\ \\ \\ \\ ("+str(count[T["equation"]])+")"
            if HTML :
                mb[1]=mb[1].replace("+","%2B")
                mb[1]=mb[1].replace(" ","+")
                mb[1]=mb[1].replace("'","&#39;")
                m = "<p align=center><img src='http://l.wordpress.com/latex.php?latex=\displaystyle " + mb[1] +endlatex+"'></p>\n"
            else :
                m = "__DISPLAYMATH_START__" + mb[1].strip() + "__DISPLAYMATH_END__"
            if m.find("\\label") != -1 :
                mnolab = label.split(m)
                mlab = label.findall(m)
                """
                 Now the mathematical equation, which has already
                 been formatted for WordPress, is the union of
                 the strings mnolab[0] and mnolab[1]. The content
                 of the \label{...} command is in mlab[0]
                """
                lab = mlab[0]
                lab=cb.split(lab)[1]
                lab=lab.replace(":","")
                ref[lab]=count[T["equation"]]

                m = "<span id=\""+lab+"\"></span>"+mnolab[0]+mnolab[1]

        R= R + [m]
    return R


def convertcolors(m,c) :
    if m.find("begin") != -1 :
        return("<span style=\"color:#"+colors[c]+";\">")
    else :
        return("</span>")


def convertitm(m) :
    if m.find("begin") != -1 :
        return ("\n\n<!-- wp:list -->\n<ul>")
    else :
        return ("\n</ul>\n<!-- /wp:list -->\n\n")

def convertenum(m) :
    if m.find("begin") != -1 :
        return ("\n\n<!-- wp:list {\"ordered\":true} -->\n<ol>")
    else :
        return ("\n</ol>\n<!-- /wp:list -->\n\n")

def convertthm(m,n,s) :
    global inthm

    if m.find("\\begin") != -1 :
        count[T[s]] = count[T[s]] + 1
        inthm = s
        if n=="" :
            t = beginthm.replace("_ThmType_",s.capitalize())
            t = t.replace("_ThmNumb_",str(count[T[s]]))
            return(t)
        else :
            t = beginnamedthm.replace("_ThmType_",s.capitalize())
            t = t.replace("_ThmNumb_",str(count[T[s]]))
            t = t.replace("_ThmName_",n[1:-1])
            return(t)
    else :
        inthm = ""
        return(endthm)

def convertem(m) :
    m=m.replace("{\\em ","<em>")
    m=m.replace("}","</em>")
    return m

def convertbf(m) :
    m=m.replace("{\\bf ","<strong>")
    m=m.replace("}","</strong>")
    return m


def convertlab(m) :
    global inthm
    global ref

    
    m=cb.split(m)[1]
    m=m.replace(":","")
    if inthm != "" :
        ref[m]=count[T[inthm]]
    else :
        ref[m]=count[T["section"]]
    return("<span id=\""+m+"\"></span>")
        


def convertproof(m) :
    if m.find("begin") != -1 :
        return(beginproof)
    else :
        return(endproof)
    

def convertsection (m) :

 
      L=cb.split(m)

      """
        L[0] contains the \\section or \\section* command, and
        L[1] contains the section name
      """

      if L[0].find("*") == -1 :
          t=section
          count[T["section"]] = count[T["section"]]+1
          count[T["subsection"]]=0

      else :
          t=sectionstar

      t=t.replace("_SecNumb_",str(count[T["section"]]) )
      t=t.replace("_SecName_",L[1])
      return(t)

def convertsubsection (m) :

      
        L=cb.split(m)

        if L[0].find("*") == -1 :
            t=subsection
        else :
            t=subsectionstar
        
        count[T["subsection"]]=count[T["subsection"]]+1
        t=t.replace("_SecNumb_",str(count[T["section"]]) )
        t=t.replace("_SubSecNumb_",str(count[T["subsection"]]) )
        t=t.replace("_SecName_",L[1])     
        return(t)


def converturl (m) :
    L = cb.split(m)
    return ("<a href=\""+L[1]+"\">"+L[3]+"</a>")

def converturlnosnap (m) :
    L = cb.split(m)
    return ("<a class=\"snap_noshots\" href=\""+L[1]+"\">"+L[3]+"</a>")


def convertimage (m) :
    L = cb.split (m)
    return ("<!-- wp:image -->\n<figure class=\"wp-block-image\"><img "+L[1] + " src=\""+L[3]
         +"\" /></figure>\n<!-- /wp:image -->")

def convertstrike (m) :
    L=cb.split(m)
    return("<s>"+L[1]+"</s>")

def processtext ( t ) :
    
        global ref


        p = re.compile("\\\\begin\\{\\w+}"
                   "|\\\\end\\{\\w+}"
                   "|\\\\item"
                   "|\\{\\\\em.*?}"
                   "|\\{\\\\bf.*?}"
                   "|\\\\label\s*\\{.*?}"
                   "|\\\\section\s*\\{.*?}"
                   "|\\\\section\\*\s*\\{.*?}"
                   "|\\\\subsection\s*\\{.*?}"
                   "|\\\\subsection\\*\s*\\{.*?}"
                   "|\\\\href\s*\\{.*?}\s*\\{.*?}"
                   "|\\\\hrefnosnap\s*\\{.*?}\s*\\{.*?}"
                   "|\\\\image\s*\\{.*?}\s*\\{.*?}\s*\\{.*?}"
                   "|\\\\sout\s*\\{.*?}"
                   "|\\[.*?\\]")


        t=t.replace("\\\\","<br>\n")
        t=t.replace("~"," ")
        t=t.replace("\\ "," ")
        
        ttext = p.split(t)
        tcontrol = p.findall(t)

 
        w = ttext[0]
 
        i=0
        while i < len(tcontrol) :
            if tcontrol[i].find("{itemize}") != -1 :
                w=w+convertitm(tcontrol[i])
            elif tcontrol[i].find("{enumerate}") != -1 :
                w= w+convertenum(tcontrol[i])
            elif tcontrol[i]=="\\item" :
                w=w+"<li>"
                if tcontrol[i+1][0] == "[" and ttext[i+1].strip() == "" :
                    w=w+tcontrol[i+1][1:-1]
                    i=i+1
            elif tcontrol[i].find("\\hrefnosnap") != -1 :
                w = w+converturlnosnap(tcontrol[i])
            elif tcontrol[i].find("\\href") != -1 :
                w = w+converturl(tcontrol[i])
            elif tcontrol[i].find("{proof}") != -1 :
                w = w+convertproof(tcontrol[i])
            elif tcontrol[i].find("\\subsection") != -1 :
                w = w+convertsubsection(tcontrol[i])
            elif tcontrol[i].find("\\section") != -1 :
                w = w+convertsection(tcontrol[i])
            elif tcontrol[i].find("\\em") != -1:
                w = w+convertem(tcontrol[i])
            elif tcontrol[i].find("\\bf") != -1:
                w = w+convertbf(tcontrol[i])
            elif tcontrol[i].find("\\label") != -1 :
                w=w+convertlab(tcontrol[i])
            elif tcontrol[i].find("\\image") != -1 :
                w = w+convertimage(tcontrol[i])
            elif tcontrol[i].find("\\sout") != -1 :
                w = w+convertstrike(tcontrol[i])
            elif tcontrol[i].find("\\begin") !=-1 and tcontrol[i].find("{center}")!= -1 :
                w = w+"<!-- wp:paragraph {\"align\":\"center\"} -->\n<p class=\"has-text-align-center\">"
            elif tcontrol[i].find("\\end")!= -1  and tcontrol[i].find("{center}") != -1 :
                w = w+"</p>\n<!-- /wp:paragraph -->"
            elif tcontrol[i][0] == "[" :
                w=w+tcontrol[i]
            else :
              for clr in colorchoice :
                if tcontrol[i].find("{"+clr+"}") != -1:
                    w=w + convertcolors(tcontrol[i],clr)
              for thm in ThmEnvs :
                if tcontrol[i]=="\\end{"+thm+"}" :
                    w=w+convertthm(tcontrol[i],"",thm)
                elif tcontrol[i]== "\\begin{"+thm+"}":
                    if ttext [i+1].strip() == "" and  tcontrol[i+1][0]=="["  :
                        w=w+convertthm(tcontrol[i],tcontrol[i+1],thm)
                        i=i+1
                    else :
                        w=w+convertthm(tcontrol[i],"",thm)
            w= w+ttext[i+1]
            i=i+1
        return(w)
    

def _make_inline_math(latex) :
    """Create an inline <math> element from raw LaTeX with MathML."""
    escaped = latex.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    data_attr = latex.replace("&","&amp;").replace('"',"&quot;").replace("<","&lt;").replace(">","&gt;")
    # Generate MathML body from LaTeX
    try :
        mathml = latex2mathml.converter.convert(latex)
        # Extract inner content between <math ...> and </math>
        inner = re.sub(r'^<math[^>]*>', '', mathml)
        inner = re.sub(r'</math>$', '', inner)
    except :
        inner = "<mrow></mrow>"
    return ("<math data-latex=\"" + data_attr + "\"><semantics>"
            + inner
            + "<annotation encoding=\"application/x-tex\">" + escaped + "</annotation>"
            "</semantics></math>")

def _split_display_math(latex, threshold=100) :
    """Split a long display math formula into two lines at a relation operator.
    Returns a list of one or two LaTeX strings.  The second line starts with
    the relation operator, mirroring how Terry Tao's blog formats wide formulas
    as consecutive centered blocks."""
    if len(latex) < threshold :
        return [latex]

    # Relation operators to break at (longest first to avoid partial matches)
    relations = ['\\leqslant', '\\geqslant', '\\leq', '\\geq',
                 '\\le', '\\ge', '\\neq', '\\sim', '=', '<', '>']

    # Find all relation operators at brace depth 0
    breakpoints = []
    depth = 0
    i = 0
    while i < len(latex) :
        if latex[i] == '{' :
            depth += 1
            i += 1
        elif latex[i] == '}' :
            depth -= 1
            i += 1
        elif depth == 0 :
            matched = False
            for rel in relations :
                if latex[i:i+len(rel)] == rel :
                    # For single-char operators, skip if preceded by backslash
                    if len(rel) == 1 and i > 0 and latex[i-1] == '\\' :
                        break
                    breakpoints.append((i, rel))
                    i += len(rel)
                    matched = True
                    break
            if not matched :
                i += 1
        else :
            i += 1

    if not breakpoints :
        return [latex]

    # Choose the breakpoint closest to the middle
    mid = len(latex) / 2
    best = min(breakpoints, key=lambda bp: abs(bp[0] - mid))

    pos, rel = best
    first = latex[:pos].strip()
    second = (rel + latex[pos+len(rel):]).strip()

    return [first, second]

def _make_math_block(latex) :
    """Create a wp:math Gutenberg block from raw LaTeX."""
    block_attrs = json.dumps({"latex": latex})
    annotation = latex.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return ("<!-- wp:math " + block_attrs + " -->\n"
            "<div class=\"wp-block-math\"><math display=\"block\"><semantics><mrow></mrow>"
            "<annotation encoding=\"application/x-tex\">" + annotation + "</annotation>"
            "</semantics></math></div>\n"
            "<!-- /wp:math -->")

def _wrap_segments(text) :
    """Split text on __PARA__ and __DISPLAYMATH__ markers, wrapping each
    segment as a wp:paragraph or wp:math block.  Auto-balances <em> tags
    that span across display math boundaries."""
    dm_re = re.compile(r'__DISPLAYMATH_START__(.*?)__DISPLAYMATH_END__', re.DOTALL)
    tag_re = re.compile(r'<[^>]+>')
    out = []
    segments = text.split("__PARA__")
    for seg in segments :
        stripped = seg.strip()
        if not stripped :
            continue
        dm_parts = dm_re.split(stripped)
        for j, dp in enumerate(dm_parts) :
            dp_stripped = dp.strip()
            if not dp_stripped :
                continue
            if j % 2 == 1 :
                for piece in _split_display_math(dp_stripped) :
                    out.append(_make_math_block(piece))
            else :
                # Skip segments that are only closing tags with no real content
                text_only = tag_re.sub('', dp_stripped).strip()
                open_em = dp_stripped.count("<em>")
                close_em = dp_stripped.count("</em>")
                if close_em > open_em and not text_only :
                    continue
                # Auto-close unclosed <em> tags
                if open_em > close_em :
                    dp_stripped = dp_stripped + "</em>" * (open_em - close_em)
                out.append("<!-- wp:paragraph -->\n<p>" + dp_stripped + "</p>\n<!-- /wp:paragraph -->")
    return "\n\n".join(out)

def gutenbergify(s) :
    """
    Post-processing pass that wraps content in Gutenberg blocks.

    1. Quote regions (__QUOTE_START__...__QUOTE_END__) become wp:quote blocks
       with inner wp:paragraph and wp:math blocks.
    2. Remaining Gutenberg blocks (headings, tables, images, etc.) are preserved.
    3. Loose text is split on __PARA__ and wrapped in wp:paragraph blocks.
    4. Display math markers become wp:math blocks.
    """

    # Step 1: Process quote blocks and replace with placeholders
    quote_blocks = []
    quote_re = re.compile(r'__QUOTE_START__(.*?)__QUOTE_END__', re.DOTALL)

    def process_quote(match) :
        content = match.group(1)
        inner = _wrap_segments(content)
        idx = len(quote_blocks)
        placeholder = "<!-- wp:__qp_" + str(idx) + "__ --><!-- /wp:__qp_" + str(idx) + "__ -->"
        quote_blocks.append(
            "<!-- wp:quote -->\n<blockquote class=\"wp-block-quote\">"
            + inner
            + "</blockquote>\n<!-- /wp:quote -->")
        return placeholder

    s = quote_re.sub(process_quote, s)

    # Step 2: Split on existing Gutenberg blocks and wrap loose text
    block_re = re.compile(r'(<!-- wp:\S+.*?-->.*?<!-- /wp:\S+? -->)', re.DOTALL)
    parts = block_re.split(s)
    out = []
    for part in parts :
        if block_re.match(part) :
            out.append(part)
        else :
            out.append(_wrap_segments(part))
    result = "\n\n".join(out)

    # Step 3: Restore quote block placeholders
    for i, qb in enumerate(quote_blocks) :
        placeholder = "<!-- wp:__qp_" + str(i) + "__ --><!-- /wp:__qp_" + str(i) + "__ -->"
        result = result.replace(placeholder, qb)

    return result


def convertref(m) :
    global ref
    
    p=re.compile("\\\\ref\s*\\{.*?}|\\\\eqref\s*\\{.*?}")

    T=p.split(m)
    M=p.findall(m)

    w = T[0]
    for i in range(len(M)) :
        t=M[i]
        lab=cb.split(t)[1]
        lab=lab.replace(":","")
        if t.find("\\eqref") != -1 :
           w=w+"<a href=\"#"+lab+"\">("+str(ref[lab])+")</a>"
        else :
           w=w+"<a href=\"#"+lab+"\">"+str(ref[lab])+"</a>"
        w=w+T[i+1]
    return w

"""
The program makes several passes through the input.

In a first clean-up, all text before \begin{document}
and after \end{document}, if present, is removed,
all double-returns are converted
to <p>, and all remaining returns are converted to
spaces.

The second step implements a few simple macros. The user can
add support for more macros if desired by editing the
convertmacros() procedure.

Then the program separates the mathematical
from the text parts. (It assumes that the document does
not start with a mathematical expression.) 

It makes one pass through the text part, translating
environments such as theorem, lemma, proof, enumerate, itemize,
\em, and \bf. Along the way, it keeps counters for the current
section and subsection and for the current numbered theorem-like
environment, as well as a  flag that tells whether one is
inside a theorem-like environment or not. Every time a \label{xx}
command is encountered, we give ref[xx] the value of the section
in which the command appears, or the number of the theorem-like
environment in which it appears (if applicable). Each appearence
of \label is replace by an html "name" tag, so that later we can
replace \ref commands by clickable html links.

The next step is to make a pass through the mathematical environments.
Displayed equations are numbered and centered, and when a \label{xx}
command is encountered we give ref[xx] the number of the current
equation. 

A final pass replaces \ref{xx} commands by the number in ref[xx],
and a clickable link to the referenced location.
"""


inputfile = "wpress.tex"
outputfile = "wpress.html"
if len(argv) > 1 :
    inputfile = argv[1]
    if len(argv) > 2 :
        outputfile = argv[2]
    else :
        outputfile = inputfile.replace(".tex",".html")
f=open(inputfile)
s=f.read()
f.close()


"""
  extractbody() takes the text between a \begin{document}
  and \end{document}, if present, (otherwise it keeps the
  whole document), normalizes the spacing, and removes comments
"""
s=extractbody(s)

# formats tables
s=converttables(s)

# converts escape sequences such as \$ to HTML codes
# This must be done after formatting the tables or the '&' in
# the HTML codes will create problems

for e in esc :
    s=s.replace(e[1],e[0])

#implement simple macros
s=convertmacros(s)


# extracts the math parts, and replaces the with placeholders
# processes math and text separately, then puts the processed
# math equations in place of the placeholders

(math,text) = separatemath(s) 


s=text[0]
for i in range(len(math)) :
    s=s+"__math"+str(i)+"__"+text[i+1]
    
s = processtext ( s )
math = processmath ( math )

for i in range(len(math)) :
    s=s.replace("__math"+str(i)+"__",math[i])

# translating the \ref{} commands
s=convertref(s)

if not HTML :
    s = gutenbergify(s)
else :
    s="<head><style>body{max-width:55em;}a:link{color:#4444aa;}a:visited{color:#4444aa;}a:hover{background-color:#aaaaFF;}</style></head><body>"+s+"</body></html>"
    s = s.replace("__PARA__","\n<p>\n")


f=open(outputfile,"w")
f.write(s)
f.close()
