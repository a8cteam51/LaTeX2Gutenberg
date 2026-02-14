# Lines starting with #, like this one, are comments

# change to HTML = True to produce standard HTML
HTML = False

# color of LaTeX formulas
textcolor = "000000"

# colors that can be used in the text
colors = { "red" : "ff0000" , "green" : "00ff00" , "blue" : "0000ff" }
# list of colors defined above
colorchoice = ["red","green","blue"]

# counters for theorem-like environments
# assign any counter to any environment. Make sure that
# maxcounter is an upper bound to the any counter being used
maxcounter = 7
T = { "theorem" : 0 , "lemma" : 0 , "proposition" : 0, "definition" : 0,
               "corollary" : 0, "remark" : 7 , "example" : 1, "claim" : 6,
               "exercise" : 2 , "section" : 3 , "subsection" : 4,
               "equation" : 5  }
# list of theorem-like environments defined above
ThmEnvs = ["theorem","definition","lemma","proposition","corollary","claim",
           "remark","example","exercise"]

# the way \begin{theorem}, \begin{lemma} etc are translated in HTML
# the string _ThmType_ stands for the type of theorem
# the string _ThmNumb_ is the theorem number
beginthm = "\n__QUOTE_START__<strong>_ThmType_ _ThmNumb_</strong> "

# translation of \begin{theorem}[...]. The string
# _ThmName_ stands for the content betwee the
# square brackets
beginnamedthm = "\n__QUOTE_START__<strong>_ThmType_ _ThmNumb_ (_ThmName_)</strong> "

#translation of \end{theorem}, \end{lemma}, etc.
endthm = "__QUOTE_END__\n"


beginproof = "<em>Proof:</em> "
endproof = "$latex \Box&fg=000000$\n\n"

section = "\n<!-- wp:heading {\"level\":2} -->\n<h2>&mdash; _SecNumb_. _SecName_ &mdash;</h2>\n<!-- /wp:heading -->\n"
sectionstar = "\n<!-- wp:heading {\"level\":2} -->\n<h2>&mdash; _SecName_ &mdash;</h2>\n<!-- /wp:heading -->\n"
subsection = "\n<!-- wp:heading {\"level\":3} -->\n<h3>&mdash; _SecNumb_._SubSecNumb_. _SecName_ &mdash;</h3>\n<!-- /wp:heading -->\n"
subsectionstar = "\n<!-- wp:heading {\"level\":3} -->\n<h3>&mdash; _SecName_ &mdash;</h3>\n<!-- /wp:heading -->\n"


# Macro definitions
# It is a sequence of pairs [string1,string2], and
# latex2wp will replace each occurrence of string1 with an
# occurrence of string2. The substitutions are performed
# in the same order as the pairs appear below.
# Feel free to add your own.
# Note that you have to write \\ instead of \
# and \" instead of "

M = [     ["\\to","\\rightarrow"] ,
          ["\\B","\\{ 0,1 \\}" ],
          ["\\E","\mathop{\\mathbb E}"],
          ["\\P","\mathop{\\mathbb P}"],
          ["\\N","{\\mathbb N}"],
          ["\\Z","{\\mathbb Z}"],
          ["\\C","{\\mathbb C}"],
          ["\\R","{\\mathbb R}"],
          ["\\xor","\\oplus"],
          ["\\epsilon","\\eps"],
          ["\\eps","\\epsilon"]
    ]

