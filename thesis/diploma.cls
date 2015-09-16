%%
%% This is file `diploma.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% VersionInfo.dtx 
%% Introduction.dtx 
%% UserManual.dtx 
%% Implementation.dtx 
%% 
%% IMPORTANT NOTICE:
%% 
%% For the copyright see the source file.
%% 
%% Any modified versions of this file must be renamed
%% with new filenames distinct from diploma.cls.
%% 
%% For distribution of the original source see the terms
%% for copying and modification in the file VersionInfo.dtx Introduction.dtx UserManual.dtx Implementation.dtx.
%% 
%% This generated file may be distributed as long as the
%% original source files, as listed above, are part of the
%% same distribution. (The sources need not necessarily be
%% in the same archive or directory.)
\def\fileversion{3.21}
\def\filedate{2014/04/25}
\def\docdate{25. dubna 2014}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{diploma}[\filedate\space v\fileversion\space diploma LaTeX document class]
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{ifthen}
\newtoks\Dipl@DiplomaTypeName
\Dipl@DiplomaTypeName={Chybí textová reprezentace typu práce}
\newtoks\Dipl@Department
\Dipl@Department={Katedra informatiky}
\newtoks\Dipl@Author
\Dipl@Author={Chybí autor}
\newtoks\Dipl@Title
\Dipl@Title={Chybí název práce}
\newtoks\Dipl@EnglishTitle
\Dipl@EnglishTitle={Chybí anglický název práce}
\newtoks\Dipl@SubmissionDate
\Dipl@SubmissionDate={Chybí datum odevzdání práce}
\newtoks\Dipl@AccessRestriction
\Dipl@AccessRestriction={}
\newtoks\Dipl@ThesisAssignmentImagePath
\Dipl@ThesisAssignmentImagePath={}
\newtoks\Dipl@DeclarationImageFile
\Dipl@DeclarationImageFile={}
\newtoks\Dipl@Thanks
\Dipl@Thanks={}
\newtoks\Dipl@CzechAbstract
\Dipl@CzechAbstract={Chybí český abstrakt}
\newtoks\Dipl@CzechKeywords
\Dipl@CzechKeywords={Chybí česká klíčová slova}
\newtoks\Dipl@EnglishAbstract
\Dipl@EnglishAbstract={Chybí anglický abstrakt}
\newtoks\Dipl@EnglishKeywords
\Dipl@EnglishKeywords={Chybí anglická klíčová slova}
\newtoks\Dipl@Acronyms
\Dipl@Acronyms={}
\newtoks\Dipl@DefaultLanguage
\Dipl@DefaultLanguage={java}
\newboolean{Dipl@AuthorIsMale}
\setboolean{Dipl@AuthorIsMale}{true}
\newboolean{Dipl@IsMasterThesis}
\setboolean{Dipl@IsMasterThesis}{true}
\newboolean{Dipl@IsBachelorPractice}
\setboolean{Dipl@IsBachelorPractice}{false}
\newboolean{Dipl@PrintPublAgreement}
\setboolean{Dipl@PrintPublAgreement}{false}
\newcounter{Dipl@ThesisAssignmentImageCounter}
\DeclareOption{bc}{\Dipl@DiplomaTypeName={Bakalářská práce}\setboolean{Dipl@IsMasterThesis}{false}\setboolean{Dipl@IsBachelorPractice}{false}}
\DeclareOption{bcpraxe}{\Dipl@DiplomaTypeName={Bakalářská práce}\setboolean{Dipl@IsMasterThesis}{false}\setboolean{Dipl@IsBachelorPractice}{true}}
\DeclareOption{ing}{\Dipl@DiplomaTypeName={Diplomová práce}\setboolean{Dipl@IsMasterThesis}{true}\setboolean{Dipl@IsBachelorPractice}{false}}
\DeclareOption{dept410}{\Dipl@Department={Katedra elektroenergetiky}}
\DeclareOption{dept420}{\Dipl@Department={Katedra elektrotechniky}}
\DeclareOption{dept430}{\Dipl@Department={Katedra elektroniky}}
\DeclareOption{dept440}{\Dipl@Department={Katedra telekomunikační techniky}}
\DeclareOption{dept450}{\Dipl@Department={Katedra kybernetiky a biomedicínského inženýrství}}
\DeclareOption{dept460}{\Dipl@Department={Katedra informatiky}}
\DeclareOption{dept470}{\Dipl@Department={Katedra aplikované matematiky}}
\DeclareOption{male}{\setboolean{Dipl@AuthorIsMale}{true}}
\DeclareOption{female}{\setboolean{Dipl@AuthorIsMale}{false}}
\DeclareOption{vb}{\Dipl@DefaultLanguage={vb}}
\DeclareOption{ansic}{\Dipl@DefaultLanguage={ansic}}
\DeclareOption{cpp}{\Dipl@DefaultLanguage={cpp}}
\DeclareOption{csharp}{\Dipl@DefaultLanguage={csharp}}
\DeclareOption{delphi}{\Dipl@DefaultLanguage={delphi}}
\DeclareOption{html}{\Dipl@DefaultLanguage={html}}
\DeclareOption{idl}{\Dipl@DefaultLanguage={idl}}
\DeclareOption{corba}{\Dipl@DefaultLanguage={corba}}
\DeclareOption{java}{\Dipl@DefaultLanguage={java}}
\DeclareOption{lisp}{\Dipl@DefaultLanguage={lisp}}
\DeclareOption{make}{\Dipl@DefaultLanguage={make}}
\DeclareOption{matlab}{\Dipl@DefaultLanguage={matlab}}
\DeclareOption{pascal}{\Dipl@DefaultLanguage={pascal}}
\DeclareOption{perl}{\Dipl@DefaultLanguage={perl}}
\DeclareOption{php}{\Dipl@DefaultLanguage={php}}
\DeclareOption{python}{\Dipl@DefaultLanguage={python}}
\DeclareOption{sql}{\Dipl@DefaultLanguage={sql}}
\DeclareOption{latex}{\Dipl@DefaultLanguage={latex}}
\DeclareOption{plaintex}{\Dipl@DefaultLanguage={plaintex}}
\DeclareOption{vhdl}{\Dipl@DefaultLanguage={vhdl}}
\DeclareOption{xml}{\Dipl@DefaultLanguage={xml}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions
\LoadClass[11pt]{article}
\RequirePackage{fancyhdr}
\RequirePackage{geometry}
\RequirePackage{graphicx}
\RequirePackage{palatino}
\RequirePackage[final]{listings}
\RequirePackage{rotating}
\RequirePackage{supertabular}
\RequirePackage{theorem}
\RequirePackage[notindex,nottoc,notlot,notlof,section,numbib]{tocbibind}
\RequirePackage[a-1b]{pdfx}
\geometry{a4paper,includeheadfoot,marginparwidth=0mm,marginparsep=0mm,left=28mm,right=32mm,top=25mm,bottom=38mm,headheight=16pt}
\fancyhf{}
\fancyhead[RO,LE]{\sffamily\bfseries\thepage}
\newcommand{\ThesisAuthor}[1]{\Dipl@Author={#1}}
\newcommand{\ThesisTitle}[1]{\ifthenelse{\boolean{Dipl@IsBachelorPractice}}{\relax}{\Dipl@Title={#1}}}
\newcommand{\EnglishThesisTitle}[1]{\ifthenelse{\boolean{Dipl@IsBachelorPractice}}{\relax}{\Dipl@EnglishTitle={#1}}}
\newcommand{\SubmissionDate}[1]{\Dipl@SubmissionDate={#1}}
\newcommand{\PrintPublicationAgreement}[1]{\setboolean{Dipl@PrintPublAgreement}{#1}}
\newcommand{\AccessRestriction}[1]{\Dipl@AccessRestriction={#1}}
\newcommand{\ThesisAssignmentImagePath}[1]{\Dipl@ThesisAssignmentImagePath={#1}}
\newcommand{\DeclarationImageFile}[1]{\Dipl@DeclarationImageFile={#1}}
\newcommand{\Thanks}[1]{\Dipl@Thanks={#1}}
\newcommand{\CzechAbstract}[1]{\Dipl@CzechAbstract={#1}}
\newcommand{\CzechKeywords}[1]{\Dipl@CzechKeywords={#1}}
\newcommand{\EnglishAbstract}[1]{\Dipl@EnglishAbstract={#1}}
\newcommand{\EnglishKeywords}[1]{\Dipl@EnglishKeywords={#1}}
\newcommand{\MakeTitlePages}%
{%
  \pagestyle{empty}
  \Dipl@TitlePage
  \Dipl@ThesisAssignment
  \Dipl@Declaration
  \Dipl@WriteThanks
  \Dipl@AbstractsKeywords
  \Dipl@WriteAcronyms
  \setcounter{page}{1}
  \pagestyle{fancy}
}
\newcommand{\Dipl@ThesisTitle}[0]{\ifthenelse{\boolean{Dipl@IsBachelorPractice}}{Absolvování individuální odborné praxe}{\the\Dipl@Title}}
\newcommand{\Dipl@ThesisEnglishTitle}[0]{\ifthenelse{\boolean{Dipl@IsBachelorPractice}}{Individual Professional Practice in the Company}{\the\Dipl@EnglishTitle}}
\newcommand{\Dipl@TitlePage}
{
  \begin{center}
    \vspace*{-23mm}
    \sffamily
    {\Large{}VŠB -- Technická univerzita Ostrava\\
    Fakulta elektrotechniky a informatiky\\
    \the\Dipl@Department\\}
    \medskip
    \hrule
    \vspace{35mm}
    {\Huge\bfseries\Dipl@ThesisTitle\par}
    \bigskip
    {\Huge\bfseries\Dipl@ThesisEnglishTitle\par}
  \end{center}
  \vfill
  {\sffamily\Large\number\year\hfill\the\Dipl@Author}
  \cleardoublepage
}
\newcommand{\Dipl@ThesisAssignment}[0]
{
  \ifthenelse{\equal{\the\Dipl@ThesisAssignmentImagePath}{\empty}}
  {
    \begin{center}
      \Large\sffamily\bfseries{}Tuto stránku nahradíte v tištěné verzi práce oficiálním zadáním Vaší diplomové či bakalářské práce.
    \end{center}
    \cleardoublepage
  }
  {
    \setcounter{Dipl@ThesisAssignmentImageCounter}{1}
    \whiledo{\value{Dipl@ThesisAssignmentImageCounter}>0}
    {
      \IfFileExists{\the\Dipl@ThesisAssignmentImagePath\theDipl@ThesisAssignmentImageCounter.jpg}
      {
        \newgeometry{margin=1pt,nohead,nofoot,nomarginpar,centering}
        \thispagestyle{empty}
        \begin{center}
          \includegraphics[width=0.99\textwidth,height=0.99\textheight]{\the\Dipl@ThesisAssignmentImagePath\theDipl@ThesisAssignmentImageCounter.jpg}
        \end{center}
        \clearpage
        \restoregeometry
        \addtocounter{Dipl@ThesisAssignmentImageCounter}{1}
      }
      {
        \setcounter{Dipl@ThesisAssignmentImageCounter}{-1}
      }
    }
    \cleardoublepage
  }
}
\newcommand{\Dipl@MaleMaster}[0]{Prohlašuji, že jsem tuto diplomovou práci
  vypracoval samostatně. Uvedl jsem všechny literární prameny a publikace,
  ze kterých jsem čerpal.}
\newcommand{\Dipl@FemaleMaster}[0]{Prohlašuji, že jsem tuto diplomovou práci
  vypracovala samostatně. Uvedla jsem všechny literární prameny a publikace,
  ze kterých jsem čerpala.}
\newcommand{\Dipl@MaleBachelor}[0]{Prohlašuji, že jsem tuto bakalářskou práci
  vypracoval samostatně. Uvedl jsem všechny literární prameny a publikace,
  ze kterých jsem čerpal.}
\newcommand{\Dipl@FemaleBachelor}[0]{Prohlašuji, že jsem tuto bakalářskou práci
  vypracovala samostatně. Uvedla jsem všechny literární prameny a publikace,
  ze kterých jsem čerpala.}
\newcommand{\Dipl@BachelorPublAgreement}[0]{Souhlasím se zveřejněním
  této bakalářské práce dle požadavků čl.\ 26, odst.\ 9 \textit{Studijního a~zkušebního
  řádu pro studium v bakalářských programech VŠB-TU Ostrava}.}
\newcommand{\Dipl@MasterPublAgreement}[0]{Souhlasím se zveřejněním
  této diplomové práce dle požadavků čl.\ 26, odst.\ 9 \textit{Studijního a~zkušebního
  řádu pro studium v magisterských programech VŠB-TU Ostrava}.}
\newcommand{\Dipl@PrintRestriction}
{
  \noindent
  \ifthenelse{\boolean{Dipl@IsMasterThesis}}
  {\Dipl@MasterPublAgreement}
  {\Dipl@BachelorPublAgreement}
  \par
  \ifthenelse{\equal{\the\Dipl@AccessRestriction}{\empty}}
  {\relax}
  {\bigskip\noindent\the\Dipl@AccessRestriction\par}
  \vspace{15mm}
  \noindent{}V Ostravě \the\Dipl@SubmissionDate\hfill\hbox to50mm{\dotfill}
  \par
  \vspace{15mm}
}
\newcommand{\Dipl@Declaration}
{
  \ifthenelse{\equal{\the\Dipl@DeclarationImageFile}{\empty}}
  {
    \mbox{}\vfill
    \ifthenelse{\boolean{Dipl@PrintPublAgreement}}{\Dipl@PrintRestriction}{}
    \noindent
    \ifthenelse{\boolean{Dipl@IsMasterThesis}}%
    {\ifthenelse{\boolean{Dipl@AuthorIsMale}}{\Dipl@MaleMaster}{\Dipl@FemaleMaster}}%
    {\ifthenelse{\boolean{Dipl@AuthorIsMale}}{\Dipl@MaleBachelor}{\Dipl@FemaleBachelor}}
    \par
    \vspace{15mm}
    \noindent{}V Ostravě \the\Dipl@SubmissionDate\hfill\hbox to50mm{\dotfill}
    \cleardoublepage
  }
  {
    \newgeometry{margin=1pt,nohead,nofoot,nomarginpar,centering}
    \thispagestyle{empty}
    \begin{center}
      \includegraphics[width=0.99\textwidth,height=0.99\textheight]{\the\Dipl@DeclarationImageFile}
    \end{center}
    \cleardoublepage
    \restoregeometry
  }
}
\newcommand{\Dipl@WriteThanks}
{
  \ifthenelse{\equal{\the\Dipl@Thanks}{\empty}}{}
  {
    \mbox{}
    \vfill
    \noindent\the\Dipl@Thanks
    \vspace{15mm}
    \cleardoublepage
  }
}
\newcommand{\Dipl@AbstractsKeywords}
{
  \vspace*{20mm}
  \noindent{\sffamily\large\bfseries{}Abstrakt}\par\medskip
  \noindent\the\Dipl@CzechAbstract\par
  \bigskip
  \noindent{\sffamily\bfseries Klíčová slova:\ }
    \the\Dipl@CzechKeywords\par
  \vspace*{30mm}
  {
    \language=0
    \noindent{\sffamily\large\bfseries{}Abstract}\par\medskip
    \noindent\the\Dipl@EnglishAbstract\par
    \bigskip
    \noindent{\sffamily\bfseries Keywords:\ }
      \the\Dipl@EnglishKeywords\par
  }
  \cleardoublepage
}
\newcommand{\Dipl@AddTokens}[2]{\expandafter \global#1\expandafter{\the#1#2}}
\newcommand{\AddAcronym}[2]{\Dipl@AddTokens{\Dipl@Acronyms}{#1&--&#2\\}}
\newcommand{\Dipl@WriteAcronyms}[0]
{
  \ifthenelse{\equal{\the\Dipl@Acronyms}{\empty}}
  {}
  {
    \clearpage
    \vspace*{20mm}
    \noindent
    {\sffamily\large\bfseries{}Seznam použitých zkratek a symbolů}
    \begin{flushleft}
      \begin{supertabular}{p{0.2\textwidth}cp{0.7\textwidth}}
        \the\Dipl@Acronyms
      \end{supertabular}
    \end{flushleft}
    \cleardoublepage
  }
}
\renewcommand\section{\cleardoublepage\suppressfloats\@startsection {section}{1}{\z@}%
  {-3.5ex \@plus -1ex \@minus -.2ex}%
  {2.3ex \@plus.2ex}%
  {\normalfont\sffamily\Large\bfseries}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {1.5ex \@plus .2ex}%
  {\normalfont\sffamily\large\bfseries}}
\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {1.5ex \@plus .2ex}%
  {\normalfont\normalsize\sffamily\bfseries}}
\renewcommand\paragraph{\@startsection{paragraph}{4}{\z@}%
  {3.25ex \@plus1ex \@minus.2ex}%
  {-1em}%
  {\normalfont\normalsize\sffamily\bfseries}}
\renewcommand\subparagraph{\@startsection{subparagraph}{5}{\z@}%
  {3.25ex \@plus1ex \@minus .2ex}%
  {-1em}%
  {\normalfont\normalsize\sffamily\bfseries}}
\renewcommand\contentsname{\sffamily{}Obsah}
\renewcommand\listfigurename{\sffamily{}Seznam obrázků}
\renewcommand\listtablename{\sffamily{}Seznam tabulek}
{\theorembodyfont{\itshape}\newtheorem{definition}{Definice}[section]}
{\theorembodyfont{\itshape}\newtheorem{theorem}{Věta}[section]}
\newenvironment{proof}
  {\par\noindent\textbf{Důkaz.}}
  {\mbox{}\hspace*{5pt}\hfill\hbox{\vrule height5pt depth0pt width5pt}\par\medskip}
{\theorembodyfont{\rmfamily}\newtheorem{remark}{Poznámka}[section]}
{\theoremstyle{break}\theorembodyfont{\rmfamily}
  \newtheorem{Dipl@examplebody}{Příklad}[section]}
\newenvironment{example}
  {\begin{Dipl@examplebody}}
  {
    \nopagebreak\mbox{}\hspace*{5pt}\hfill\hbox{\vrule height5pt depth0pt width5pt}
    \end{Dipl@examplebody}
  }
\def\lstlistlistingname{\sffamily{}Seznam výpisů zdrojového kódu}
\def\lstlistingname{Výpis}
\newcommand{\Dipl@SetDefaultLanguage}[0]
{
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{vb}}
    {\lstset{language=[Visual]Basic}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{ansic}}
    {\lstset{language=[ANSI]C}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{cpp}}
    {\lstset{language=C++}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{csharp}}
    {\lstset{language=[Sharp]C}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{delphi}}
    {\lstset{language=Delphi}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{html}}
    {\lstset{language=HTML}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{idl}}
    {\lstset{language=IDL}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{corba}}
    {\lstset{language=[CORBA]IDL}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{java}}
    {\lstset{language=Java}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{lisp}}
    {\lstset{language=Lisp}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{make}}
    {\lstset{language=make}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{matlab}}
    {\lstset{language=Matlab}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{pascal}}
    {\lstset{language=Pascal}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{perl}}
    {\lstset{language=Perl}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{php}}
    {\lstset{language=PHP}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{python}}
    {\lstset{language=Python}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{sql}}
    {\lstset{language=SQL}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{latex}}
    {\lstset{language=[LaTeX]TeX}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{plaintex}}
    {\lstset{language=[plain]TeX}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{vhdl}}
    {\lstset{language=VHDL}}{}
  \ifthenelse{\equal{\the\Dipl@DefaultLanguage}{xml}}
    {\lstset{language=XML}}{}
}
\lstset%
{
  extendedchars=true,
  basicstyle=\footnotesize\sffamily,
  commentstyle=\sffamily\slshape,
  breaklines=true,
  tabsize=3,
  xleftmargin=3em,
  columns=flexible,
  print=true,
  captionpos=b,
  frame=lines,
  framexleftmargin=3em,
}
\newcommand{\InlCode}[1]{\lstinline[basicstyle=\small\sffamily]$#1$}
\def\appname{Přílohy}
\renewcommand\appendix{\par
  \setcounter{section}{0}%
  \setcounter{subsection}{0}%
  \gdef\thesection{\@Alph\c@section}
  \addcontentsline{toc}{section}{\appname}%
  }
\newcommand{\InsertFigure}[4]
{
  \begin{figure}
    \centering
    \includegraphics[width=#2]{#1}
    \caption{#3}
    \label{#4}
  \end{figure}
}
\newcommand{\InsertSidewaysFigure}[4]
{
  \begin{sidewaysfigure}
    \centering
    \includegraphics[width=#2]{#1}
    \caption{#3}
    \label{#4}
  \end{sidewaysfigure}
}
\setcounter{tocdepth}{2}
\setcounter{secnumdepth}{5}
\widowpenalty=9000
\clubpenalty=9000
\AtBeginDocument%
{
  \Dipl@SetDefaultLanguage
  \def\appname{Přílohy}
  \def\refname{Literatura}
}
\endinput
%%
%% End of file `diploma.cls'.
