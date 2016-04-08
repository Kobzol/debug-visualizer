%%
%% This is file `diploma.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% VersionInfo.dtx 
%% Introduction.dtx 
%% UserManual.dtx 
%% ImplementationBeginning.dtx 
%% Constants.dtx 
%% VariablesDeclaration.dtx 
%% BaseClassAndPackages.dtx 
%% OptionsDeclaration.dtx 
%% PublicMacros.dtx 
%% InternalMacros.dtx 
%% SourceCodeListings.dtx 
%% ImplementationFinale.dtx 
%% 
%% IMPORTANT NOTICE:
%% 
%% For the copyright see the source file.
%% 
%% Any modified versions of this file must be renamed
%% with new filenames distinct from diploma.cls.
%% 
%% For distribution of the original source see the terms
%% for copying and modification in the file VersionInfo.dtx Introduction.dtx UserManual.dtx ImplementationBeginning.dtx Constants.dtx VariablesDeclaration.dtx BaseClassAndPackages.dtx OptionsDeclaration.dtx PublicMacros.dtx InternalMacros.dtx SourceCodeListings.dtx ImplementationFinale.dtx.
%% 
%% This generated file may be distributed as long as the
%% original source files, as listed above, are part of the
%% same distribution. (The sources need not necessarily be
%% in the same archive or directory.)
\def\fileversion{3.93}
\def\filedate{2016/04/7}
\def\docdate{7. dubna 2016}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{diploma}[\filedate\space \fileversion\space diploma LaTeX document class]
\RequirePackage[utf8]{inputenc}
\RequirePackage{ifthen}
\newcommand{\Dipl@BachelorThesis}{0}
\newcommand{\Dipl@BachelorPractice}{1}
\newcommand{\Dipl@MasterThesis}{2}
\newcommand{\Dipl@PhDThesis}{3}
\newcommand{\Dipl@CzechLanguage}{0}
\newcommand{\Dipl@EnglishLanguage}{1}
\newcommand{\Dipl@SlovakLanguage}{2}
\newtoks\Dipl@UniversityName
\Dipl@UniversityName={No university name is given}
\newtoks\Dipl@FacultyName
\Dipl@FacultyName={No faculty name is given}
\newtoks\Dipl@DepartmentName
\Dipl@DepartmentName={No department name is given}
\newtoks\Dipl@ThesisAuthor
\Dipl@ThesisAuthor={No author name is given}
\newtoks\Dipl@CzechThesisTitle
\Dipl@CzechThesisTitle={No Czech or Slovak thesis title is given}
\newtoks\Dipl@EnglishThesisTitle
\Dipl@EnglishThesisTitle={No English thesis title is given}
\newtoks\Dipl@SubmissionDate
\Dipl@SubmissionDate={No submission date is given}
\newtoks\Dipl@ThesisAssignmentImagePath
\Dipl@ThesisAssignmentImagePath={}
\newtoks\Dipl@AuthorDeclaration
\Dipl@AuthorDeclaration={}
\newtoks\Dipl@AuthorDeclarationImageFile
\Dipl@AuthorDeclarationImageFile={}
\newtoks\Dipl@CooperatingPersonsDeclaration
\Dipl@CooperatingPersonsDeclaration={}
\newtoks\Dipl@ThesisAccessRestriction
\Dipl@ThesisAccessRestriction={}
\newtoks\Dipl@CooperatingPersonsDeclarationImageFile
\Dipl@CooperatingPersonsDeclarationImageFile={}
\newtoks\Dipl@Thanks
\Dipl@Thanks={}
\newtoks\Dipl@CzechAbstract
\Dipl@CzechAbstract={No Czech or Slovak abstract is given}
\newtoks\Dipl@CzechKeywords
\Dipl@CzechKeywords={No Czech or Slovak keywords are given}
\newtoks\Dipl@EnglishAbstract
\Dipl@EnglishAbstract={No English abstract is given}
\newtoks\Dipl@EnglishKeywords
\Dipl@EnglishKeywords={No English keywords are given}
\newtoks\Dipl@Acronyms
\Dipl@Acronyms={}
\newtoks\Dipl@DefaultSourceCodeLanguage
\Dipl@DefaultSourceCodeLanguage={java}
\newboolean{Dipl@IsPublicPart}
\setboolean{Dipl@IsPublicPart}{true}
\newboolean{Dipl@AuthorIsMale}
\setboolean{Dipl@AuthorIsMale}{true}
\newboolean{Dipl@PrintCooperatingPersonsDeclaration}
\setboolean{Dipl@PrintCooperatingPersonsDeclaration}{false}
\newboolean{Dipl@IsAppendix}
\setboolean{Dipl@IsAppendix}{false}
\newcounter{Dipl@CurrentThesisType}
\setcounter{Dipl@CurrentThesisType}{\Dipl@MasterThesis}
\newcounter{Dipl@CurrentThesisLanguage}
\setcounter{Dipl@CurrentThesisLanguage}{\Dipl@CzechLanguage}
\newcounter{Dipl@ThesisAssignmentImageCounter}
\LoadClass[11pt]{article}
\RequirePackage[english,slovak,main=czech]{babel}
\RequirePackage[T1]{fontenc}
\RequirePackage{lmodern}
\RequirePackage[a4paper,includefoot,nohead,marginparwidth=0mm,marginparsep=0mm,left=30mm,right=20mm,top=30mm,bottom=30mm]{geometry}
\RequirePackage{booktabs}
\RequirePackage{graphicx}
\RequirePackage[final]{listings}
\RequirePackage{longtable}
\RequirePackage{rotating}
\RequirePackage{setspace}
\RequirePackage{theorem}
\RequirePackage{titlesec}
\RequirePackage[nottoc,notindex,section]{tocbibind}
\RequirePackage{totcount}
\RequirePackage{xcolor}
\RequirePackage[a-1b]{pdfx}
\DeclareOption{czech}
{
\setcounter{Dipl@CurrentThesisLanguage}{\Dipl@CzechLanguage}
\Dipl@UniversityName={VŠB -- Technická univerzita Ostrava}
\Dipl@FacultyName={Fakulta elektrotechniky a informatiky}
}
\DeclareOption{english}
{
\setcounter{Dipl@CurrentThesisLanguage}{\Dipl@EnglishLanguage}
\Dipl@UniversityName={VŠB -- Technical University of Ostrava}
\Dipl@FacultyName={Faculty of Electrical Engineering and Computer Science}
}
\DeclareOption{slovak}
{
\setcounter{Dipl@CurrentThesisLanguage}{\Dipl@SlovakLanguage}
\Dipl@UniversityName={VŠB -- Technická univerzita Ostrava}
\Dipl@FacultyName={Fakulta elektrotechniky a informatiky}
}
\DeclareOption{bachelor}
{
\setcounter{Dipl@CurrentThesisType}{\Dipl@BachelorThesis}
\Dipl@CooperatingPersonsDeclaration={\Dipl@IfEnglish{I hereby agree to the publishing of the bachelor's thesis as per s. 26, ss. 9 of the Study and Examination Regulations for Bachelor's Degree Programmes at VŠB -- Technical University of Ostrava.}{Souhlasím se zveřejněním této bakalářské práce dle požadavků čl.\ 26, odst.\ 9 Studijního a~zkušebního řádu pro studium v bakalářských programech VŠB-TU Ostrava.}}
}
\DeclareOption{bachelorpractice}
{
\setcounter{Dipl@CurrentThesisType}{\Dipl@BachelorPractice}
\Dipl@CzechThesisTitle={Absolvování individuální odborné praxe}
\Dipl@EnglishThesisTitle={Individual Professional Practice in the Company}
\Dipl@CooperatingPersonsDeclaration={\Dipl@IfEnglish{I hereby agree to the publishing of the bachelor's thesis as per s. 26, ss. 9 of the Study and Examination Regulations for Bachelor's Degree Programmes at VŠB -- Technical University of Ostrava.}{Souhlasím se zveřejněním této bakalářské práce dle požadavků čl.\ 26, odst.\ 9 Studijního a~zkušebního řádu pro studium v bakalářských programech VŠB-TU Ostrava.}}
}
\DeclareOption{master}
{
\setcounter{Dipl@CurrentThesisType}{\Dipl@MasterThesis}
\Dipl@CooperatingPersonsDeclaration={\Dipl@IfEnglish{I hereby agree to the publishing of the master's thesis as per s. 26, ss. 9 of the Study and Examination Regulations for Master's Degree Programmes at VŠB -- Technical University of Ostrava.}{Souhlasím se zveřejněním této diplomové práce dle požadavků čl.\ 26, odst.\ 9 Studijního a~zkušebního řádu pro studium v magisterských programech VŠB-TU Ostrava.}}
}
\DeclareOption{phd}{\setcounter{Dipl@CurrentThesisType}{\Dipl@PhDThesis}}
\DeclareOption{public}{\setboolean{Dipl@IsPublicPart}{true}}
\DeclareOption{nonpublic}{\setboolean{Dipl@IsPublicPart}{false}}
\DeclareOption{cpdeclaration}{\setboolean{Dipl@PrintCooperatingPersonsDeclaration}{true}}
\DeclareOption{dept410}{\Dipl@DepartmentName={\Dipl@IfEnglish{Department of Electrical Power Engineering}{Katedra elektroenergetiky}}}
\DeclareOption{dept420}{\Dipl@DepartmentName={\Dipl@IfEnglish{Department of Electrical Engineering}{Katedra elektrotechniky}}}
\DeclareOption{dept430}{\Dipl@DepartmentName={\Dipl@IfEnglish{Department of Electronics}{Katedra elektroniky}}}
\DeclareOption{dept440}{\Dipl@DepartmentName={\Dipl@IfEnglish{Department of Telecommunications}{Katedra telekomunikační techniky}}}
\DeclareOption{dept450}{\Dipl@DepartmentName={\Dipl@IfEnglish{Department of Cybernetics and Biomedical Engineering}{Katedra kybernetiky a biomedicínského inženýrství}}}
\DeclareOption{dept460}{\Dipl@DepartmentName={\Dipl@IfEnglish{Department of Computer Science}{Katedra informatiky}}}
\DeclareOption{dept470}{\Dipl@DepartmentName={\Dipl@IfEnglish{Department of Applied Mathematics}{Katedra aplikované matematiky}}}
\DeclareOption{male}
{
\setboolean{Dipl@AuthorIsMale}{true}
\ifthenelse{\(\value{Dipl@CurrentThesisType}=\Dipl@BachelorThesis\) \or \(\value{Dipl@CurrentThesisType}=\Dipl@BachelorPractice\)}
{
\Dipl@AuthorDeclaration={\Dipl@IfEnglish{I hereby declare that this bachelor's thesis was written by myself. I have quoted all the references I have drawn upon.}{Prohlašuji, že jsem tuto bakalářskou práci vypracoval samostatně. Uvedl jsem všechny literární prameny a publikace, ze kterých jsem čerpal.}}
}
{\relax}
\ifthenelse{\value{Dipl@CurrentThesisType}=\Dipl@MasterThesis}
{

\Dipl@AuthorDeclaration={\Dipl@IfEnglish{I hereby declare that this master's thesis was written by myself. I have quoted all the references I have drawn upon.}{Prohlašuji, že jsem tuto diplomovou práci vypracoval samostatně. Uvedl jsem všechny literární prameny a publikace, ze kterých jsem čerpal.}}
}
{\relax}
}
\DeclareOption{female}
{
\setboolean{Dipl@AuthorIsMale}{false}
\ifthenelse{\(\value{Dipl@CurrentThesisType}=\Dipl@BachelorThesis\) \or \(\value{Dipl@CurrentThesisType}=\Dipl@BachelorPractice\)}
{
\Dipl@AuthorDeclaration={\Dipl@IfEnglish{I hereby declare that this bachelor's thesis was written by myself. I have quoted all the references I have drawn upon.}{Prohlašuji, že jsem tuto bakalářskou práci vypracovala samostatně. Uvedla jsem všechny literární prameny a publikace, ze kterých jsem čerpala.}}
}
{\relax}
\ifthenelse{\value{Dipl@CurrentThesisType}=\Dipl@MasterThesis}
{
\Dipl@AuthorDeclaration={\Dipl@IfEnglish{I hereby declare that this master's thesis was written by myself. I have quoted all the references I have drawn upon.}{Prohlašuji, že jsem tuto diplomovou práci vypracovala samostatně. Uvedla jsem všechny literární prameny a publikace, ze kterých jsem čerpala.}}
}
{\relax}
}
\DeclareOption{ansic}{\Dipl@DefaultSourceCodeLanguage={ansic}}
\DeclareOption{bash}{\Dipl@DefaultSourceCodeLanguage={bash}}
\DeclareOption{cil}{\Dipl@DefaultSourceCodeLanguage={cil}}
\DeclareOption{cpp}{\Dipl@DefaultSourceCodeLanguage={cpp}}
\DeclareOption{csharp}{\Dipl@DefaultSourceCodeLanguage={csharp}}
\DeclareOption{delphi}{\Dipl@DefaultSourceCodeLanguage={delphi}}
\DeclareOption{gnuplot}{\Dipl@DefaultSourceCodeLanguage={gnuplot}}
\DeclareOption{html}{\Dipl@DefaultSourceCodeLanguage={html}}
\DeclareOption{java}{\Dipl@DefaultSourceCodeLanguage={java}}
\DeclareOption{latex}{\Dipl@DefaultSourceCodeLanguage={latex}}
\DeclareOption{lisp}{\Dipl@DefaultSourceCodeLanguage={lisp}}
\DeclareOption{lua}{\Dipl@DefaultSourceCodeLanguage={lua}}
\DeclareOption{make}{\Dipl@DefaultSourceCodeLanguage={make}}
\DeclareOption{mathematica}{\Dipl@DefaultSourceCodeLanguage={mathematica}}
\DeclareOption{matlab}{\Dipl@DefaultSourceCodeLanguage={matlab}}
\DeclareOption{octave}{\Dipl@DefaultSourceCodeLanguage={octave}}
\DeclareOption{pascal}{\Dipl@DefaultSourceCodeLanguage={pascal}}
\DeclareOption{perl}{\Dipl@DefaultSourceCodeLanguage={perl}}
\DeclareOption{php}{\Dipl@DefaultSourceCodeLanguage={php}}
\DeclareOption{pov}{\Dipl@DefaultSourceCodeLanguage={pov}}
\DeclareOption{prolog}{\Dipl@DefaultSourceCodeLanguage={prolog}}
\DeclareOption{python}{\Dipl@DefaultSourceCodeLanguage={python}}
\DeclareOption{ruby}{\Dipl@DefaultSourceCodeLanguage={ruby}}
\DeclareOption{r}{\Dipl@DefaultSourceCodeLanguage={r}}
\DeclareOption{sh}{\Dipl@DefaultSourceCodeLanguage={sh}}
\DeclareOption{sql}{\Dipl@DefaultSourceCodeLanguage={sql}}
\DeclareOption{tcltk}{\Dipl@DefaultSourceCodeLanguage={tcltk}}
\DeclareOption{vb}{\Dipl@DefaultSourceCodeLanguage={vb}}
\DeclareOption{vhdl}{\Dipl@DefaultSourceCodeLanguage={vhdl}}
\DeclareOption{xml}{\Dipl@DefaultSourceCodeLanguage={xml}}
\DeclareOption{xslt}{\Dipl@DefaultSourceCodeLanguage={xslt}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions
\newcommand{\ThesisAuthor}[1]{\Dipl@ThesisAuthor={#1}}
\newcommand{\CzechThesisTitle}[1]{\ifthenelse{\value{Dipl@CurrentThesisType}=\Dipl@BachelorPractice}{\relax}{\Dipl@CzechThesisTitle={#1}}}
\newcommand{\EnglishThesisTitle}[1]{\ifthenelse{\value{Dipl@CurrentThesisType}=\Dipl@BachelorPractice}{\relax}{\Dipl@EnglishThesisTitle={#1}}}
\newcommand{\SubmissionDate}[1]{\Dipl@SubmissionDate={#1}}
\newcommand{\ThesisAssignmentImagePath}[1]{\Dipl@ThesisAssignmentImagePath={#1}}
\newcommand{\AuthorDeclarationImageFile}[1]{\Dipl@AuthorDeclarationImageFile={#1}}
\newcommand{\ThesisAccessRestriction}[1]{\Dipl@ThesisAccessRestriction={#1}}
\newcommand{\CooperatingPersonsDeclarationImageFile}[1]{\Dipl@CooperatingPersonsDeclarationImageFile={#1}}
\newcommand{\Thanks}[1]{\Dipl@Thanks={#1}}
\newcommand{\CzechAbstract}[1]{\Dipl@CzechAbstract={#1}}
\newcommand{\CzechKeywords}[1]{\Dipl@CzechKeywords={#1}}
\newcommand{\EnglishAbstract}[1]{\Dipl@EnglishAbstract={#1}}
\newcommand{\EnglishKeywords}[1]{\Dipl@EnglishKeywords={#1}}
\newcommand{\AddAcronym}[2]{\Dipl@AddTokens{\Dipl@Acronyms}{#1&--&#2\\}}
\newcommand{\MakeTitlePages}
{
\pagestyle{empty}
\Dipl@TitlePage
\Dipl@ThesisAssignmentPage
\Dipl@AuthorDeclarationPage
\Dipl@CooperatingPersonsDeclarationPage
\Dipl@WriteThanksPage
\Dipl@AbstractsKeywordsPage
\pagestyle{plain}
\tableofcontents\cleardoublepage
\Dipl@WriteAcronymsPage
\ifthenelse{\totvalue{figure}>0}{\listoffigures\cleardoublepage}{\relax}
\ifthenelse{\totvalue{table}>0}{\listoftables\cleardoublepage}{\relax}
}
{\theorembodyfont{\itshape}\newtheorem{definition}{\Dipl@IfEnglish{Definition}{Definice}}}
{\theorembodyfont{\itshape}\newtheorem{theorem}{\Dipl@IfEnglish{Theorem}{Věta}}}
\newenvironment{proof}
{\par\noindent\textbf{\Dipl@IfEnglish{Proof.}{Důkaz.}}}
{\mbox{}\hspace*{5pt}\hfill\hbox{\vrule height5pt depth0pt width5pt}\par\medskip}
{\theorembodyfont{\rmfamily}\newtheorem{remark}{\Dipl@IfEnglish{Remark}{Poznámka}}}
{\theoremstyle{break}\theorembodyfont{\rmfamily}\newtheorem{Dipl@examplebody}{\Dipl@IfEnglish{Example}{Příklad}}}
\newenvironment{example}
{\begin{Dipl@examplebody}}
{
\nopagebreak\mbox{}\hspace*{5pt}\hfill\hbox{\vrule height5pt depth0pt width5pt}
\end{Dipl@examplebody}
}
\newcommand{\InsertFigure}[4]
{
\begin{figure}[H]
\centering
\includegraphics[width=#2]{#1}
\caption{#3}
\label{#4}
\end{figure}
}
\newcommand{\InsertFigureSource}[5]
{
\begin{figure}[H]
\centering
\includegraphics[width=#2]{#1}
\caption{#3}
\label{#4}
\caption*{#5}
\end{figure}
}
\newcommand{\Dipl@TitlePage}
{
\begin{center}
\sffamily
{\Large\the\Dipl@UniversityName\par
\the\Dipl@FacultyName\par
\the\Dipl@DepartmentName\par}
\vspace{26mm}
{\Huge\bfseries\Dipl@IfEnglish{\the\Dipl@EnglishThesisTitle}{\the\Dipl@CzechThesisTitle}\par}
\bigskip
{\Huge\bfseries\Dipl@IfEnglish{\the\Dipl@CzechThesisTitle}{\the\Dipl@EnglishThesisTitle}\par}
\ifthenelse{\boolean{Dipl@IsPublicPart}}{\relax}
{
\bigskip
\bigskip
{\huge\Dipl@IfEnglish{Non-public part/Neveřejná část}{Neveřejná část/Non-public part}\par}
}
\end{center}
\vfill
{\sffamily\Large\number\year\hfill\the\Dipl@ThesisAuthor}
\cleardoublepage
}
\newcommand{\Dipl@ThesisAssignmentPage}
{
\ifthenelse{\equal{\the\Dipl@ThesisAssignmentImagePath}{\empty}}
{
\begin{center}
\Large\sffamily\bfseries
\Dipl@IfEnglish{This page will be replaced by official thesis assignment in printed and electronic version of the submitted thesis.}%
{Tuto stránku nahradíte v tištěné verzi práce oficiálním zadáním Vaší diplomové či bakalářské práce.}
\end{center}
}
{
\setcounter{Dipl@ThesisAssignmentImageCounter}{1}
\whiledo{\value{Dipl@ThesisAssignmentImageCounter}>0}
{
\IfFileExists{\the\Dipl@ThesisAssignmentImagePath\theDipl@ThesisAssignmentImageCounter.jpg}
{
\Dipl@InsertFullPageImage{\the\Dipl@ThesisAssignmentImagePath\theDipl@ThesisAssignmentImageCounter.jpg}
\addtocounter{Dipl@ThesisAssignmentImageCounter}{1}
}
{
\setcounter{Dipl@ThesisAssignmentImageCounter}{-1}
}
}
}
\cleardoublepage
}
\newcommand{\Dipl@AuthorDeclarationPage}
{
\ifthenelse{\equal{\the\Dipl@AuthorDeclarationImageFile}{\empty}}
{
\mbox{}
\vfill
\noindent
\the\Dipl@AuthorDeclaration
\par
\vspace{15mm}
\noindent\Dipl@IfEnglish{Ostrava,}{V Ostravě}~\the\Dipl@SubmissionDate\hfill\hbox to50mm{\dotfill}
}
{
\Dipl@InsertFullPageImage{\the\Dipl@AuthorDeclarationImageFile}
}
\cleardoublepage
}
\newcommand{\Dipl@CooperatingPersonsDeclarationPage}
{
\ifthenelse{\boolean{Dipl@PrintCooperatingPersonsDeclaration}}
{
\ifthenelse{\equal{\the\Dipl@CooperatingPersonsDeclarationImageFile}{\empty}}
{
\mbox{}
\vfill
\ifthenelse{\equal{\the\Dipl@ThesisAccessRestriction}{\empty}}
{\relax}
{\noindent\the\Dipl@ThesisAccessRestriction\par\bigskip}
\noindent
\the\Dipl@CooperatingPersonsDeclaration
\par
\vspace{15mm}
\noindent\Dipl@IfEnglish{Ostrava,}{V Ostravě}~\the\Dipl@SubmissionDate\hfill\hbox to50mm{\dotfill}
}
{
\Dipl@InsertFullPageImage{\the\Dipl@CooperatingPersonsDeclarationImageFile}
}
\cleardoublepage
}
{\relax}
}
\newcommand{\Dipl@WriteThanksPage}
{
\ifthenelse{\equal{\the\Dipl@Thanks}{\empty}}
{\relax}
{
\mbox{}
\vfill
\noindent\the\Dipl@Thanks
\cleardoublepage
}
}
\newcommand{\Dipl@AbstractsKeywordsPage}
{
\vspace*{20mm}
\ifthenelse{\value{Dipl@CurrentThesisLanguage}=\Dipl@CzechLanguage}
{
\begin{otherlanguage}{czech}
\noindent\textbf{Abstrakt}\par
\medskip
\noindent\the\Dipl@CzechAbstract\par
\bigskip
\noindent\textbf{Klíčová slova}:~\the\Dipl@CzechKeywords\par

\end{otherlanguage}
}
{\relax}
\ifthenelse{\value{Dipl@CurrentThesisLanguage}=\Dipl@SlovakLanguage}
{
\begin{otherlanguage}{slovak}
\noindent\textbf{Abstrakt}\par
\medskip
\noindent\the\Dipl@CzechAbstract\par
\bigskip
\noindent\textbf{Klíčová slova}:~\the\Dipl@CzechKeywords\par
 \end{otherlanguage}
}
{\relax}
\vspace*{30mm}
\begin{otherlanguage}{english}
\noindent\textbf{Abstract}\par
\medskip
\noindent\the\Dipl@EnglishAbstract\par
\bigskip
\noindent\textbf{Key Words}:~\the\Dipl@EnglishKeywords\par
\end{otherlanguage}
\cleardoublepage
}
\newcommand{\Dipl@WriteAcronymsPage}
{
\ifthenelse{\equal{\the\Dipl@Acronyms}{\empty}}
{\relax}
{
\section*{\Dipl@IfEnglish{List of symbols and abbreviations}{Seznam použitých zkratek a symbolů}}
\ifthenelse{\value{Dipl@CurrentThesisLanguage}=\Dipl@EnglishLanguage}
{
\addcontentsline{toc}{section}{List of symbols and abbreviations}
}
{
\addcontentsline{toc}{section}{Seznam použitých zkratek a symbolů}
}
\begin{longtable*}[l]{p{0.2\textwidth}cp{0.7\textwidth}}
\the\Dipl@Acronyms
\end{longtable*}
\cleardoublepage
}
}
\newcommand{\Dipl@PrintRestriction}
{
\noindent\the\Dipl@PublicationAgreement\par
\ifthenelse{\equal{\the\Dipl@AccessRestriction}{\empty}}
{\relax}
{\bigskip\noindent\the\Dipl@AccessRestriction\par}
\vspace{15mm}
\noindent\Dipl@IfEnglish{Ostrava,}{V Ostravě}~\the\Dipl@SubmissionDate\hfill\hbox to50mm{\dotfill}\par
\vspace{15mm}
}
\newcommand{\sectionbreak}
{
\cleardoublepage
\ifthenelse{\boolean{Dipl@IsAppendix}}{\relax}{\suppressfloats}
}
\let\Dipl@OldAppendix\appendix
\renewcommand{\appendix}
{
\Dipl@OldAppendix
\addcontentsline{toc}{section}{\appendixname}%
}
\newcommand{\Dipl@IfEnglish}[2]{\ifthenelse{\value{Dipl@CurrentThesisLanguage}=\Dipl@EnglishLanguage}{#1}{#2}}
\newcommand{\Dipl@AddTokens}[2]{\expandafter \global#1\expandafter{\the#1#2}}
\newcommand{\Dipl@InsertFullPageImage}[1]
{
\newgeometry{margin=1pt,nohead,nofoot,nomarginpar,centering}
\thispagestyle{empty}
\begin{center}
\includegraphics[width=0.99\textwidth,height=0.99\textheight]{#1}
\end{center}
\cleardoublepage
\restoregeometry
}
\newcommand{\Dipl@SetDefaultLanguage}
{
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{ansic}}{\lstset{language=[ANSI]C}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{bash}}{\lstset{language=bash}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{cil}}{\lstset{language=CIL}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{cpp}}{\lstset{language=C++}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{csharp}}{\lstset{language=[Sharp]C}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{delphi}}{\lstset{language=Delphi}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{gnuplot}}{\lstset{language=Gnuplot}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{html}}{\lstset{language=HTML}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{java}}{\lstset{language=Java}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{latex}}{\lstset{language=[LaTeX]TeX}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{lisp}}{\lstset{language=Lisp}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{lua}}{\lstset{language=Lua}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{make}}{\lstset{language=make}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{mathematica}}{\lstset{language=Mathematica}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{matlab}}{\lstset{language=Matlab}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{octave}}{\lstset{language=Octave}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{pascal}}{\lstset{language=Pascal}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{perl}}{\lstset{language=Perl}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{php}}{\lstset{language=PHP}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{pov}}{\lstset{language=POV}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{prolog}}{\lstset{language=Prolog}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{python}}{\lstset{language=Python}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{ruby}}{\lstset{language=Ruby}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{r}}{\lstset{language=R}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{sh}}{\lstset{language=sh}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{sql}}{\lstset{language=SQL}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{tcltk}}{\lstset{language=[tk]tcl}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{vb}}{\lstset{language=[Visual]Basic}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{vhdl}}{\lstset{language=VHDL}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{xml}}{\lstset{language=XML}}{}
\ifthenelse{\equal{\the\Dipl@DefaultSourceCodeLanguage}{xslt}}{\lstset{language=XSLT}}{}
}
\lstset
{
basicstyle=\ttfamily,
keywordstyle=\color{blue},
identifierstyle=\color[RGB]{43,145,175},
commentstyle=\slshape\color[RGB]{0,128,0},
stringstyle=\color[RGB]{163,21,21},
breaklines=true,
tabsize=3,
columns=flexible,
showstringspaces=false,
frame=lines,
captionpos=b
}
\onehalfspacing
\setcounter{tocdepth}{2}
\setcounter{secnumdepth}{5}
\widowpenalty=9000
\clubpenalty=9000
\regtotcounter{figure}
\regtotcounter{table}
\addto{\captionsczech}{\renewcommand{\refname}{Literatura}}
\addto{\captionsslovak}{\renewcommand{\refname}{Literatura}}
\addto{\captionsczech}{\renewcommand{\appendixname}{Přílohy}}
\addto{\captionsslovak}{\renewcommand{\appendixname}{Přílohy}}
\AtBeginDocument%
{
\ifthenelse{\value{Dipl@CurrentThesisLanguage}=\Dipl@CzechLanguage}
{
\selectlanguage{czech}
\def\lstlistlistingname{\sffamily{}Seznam výpisů zdrojového kódu}
\def\lstlistingname{Výpis}
}{}
\ifthenelse{\value{Dipl@CurrentThesisLanguage}=\Dipl@EnglishLanguage}
{
\selectlanguage{english}
}{}
\ifthenelse{\value{Dipl@CurrentThesisLanguage}=\Dipl@SlovakLanguage}
{
\selectlanguage{slovak}
\def\lstlistlistingname{\sffamily{}Seznam výpisů zdrojového kódu}
\def\lstlistingname{Výpis}
}{}
\Dipl@SetDefaultLanguage
}
\endinput
%%
%% End of file `diploma.cls'.
