\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{wlscirep}[2026/07/08 local compatibility class for Scientific Reports submissions]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions*
\LoadClass{article}
\RequirePackage[letterpaper,left=2cm,right=2cm,top=2.25cm,bottom=2.25cm]{geometry}
\RequirePackage{authblk}
\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage{booktabs}
\RequirePackage{amsmath,amssymb,amsfonts}
\RequirePackage{caption}
\RequirePackage[colorlinks=true,allcolors=blue]{hyperref}
\RequirePackage[nospace,biblabel]{cite}
\renewcommand\Authfont{\fontsize{12}{12}\selectfont\bfseries}
\renewcommand\Affilfont{\fontsize{10}{12}\selectfont}
\setlength{\affilsep}{1.2em}
\renewcommand{\maketitle}{%
  \begin{flushleft}
  {\Large\bfseries \@title\par}
  \vspace{0.75em}
  {\@author\par}
  \vspace{1em}
  {\bfseries ABSTRACT}\par
  \vspace{0.3em}
  \theabstract
  \vspace{1.2em}
  \end{flushleft}
}
\def\xabstract{abstract}
\long\def\abstract#1\end#2{\def\two{#2}\ifx\two\xabstract
\long\gdef\theabstract{\ignorespaces#1}
\def\go{\end{abstract}}\else
#1\end{#2}
\gdef\theabstract{BADLY FORMED ABSTRACT}\let\go\relax\fi
\go}
