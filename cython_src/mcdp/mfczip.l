%option noyywrap yylineno

%{
    #include <string.h>
    #include <stdint.h>

    //#define USE_PY
    
    enum {
        CMD=1, LITERAL, STR, NUM, PATH,
        S_VER, S_PRAGMA, S_PACK, S_INIT, S_ENTER, S_EXIT, S_FILE, S_FUNC, S_TAG,
        CLN, CMA, SLP, SRP
    } TokenSyn;

    enum {
        MSG, OPT,
        ON, OFF
    } PragmaArg;

    typedef struct {
        int syn;
        void* val;
    } Token;

    typedef void (*T_F_Pragma)(void);

    #ifdef USE_PY
    #include "mcfunczip.h"
    #define YY_FATAL_ERROR(msg) mfczip_err(mfczip_lineon, msg)
    #endif

    #define ECHO {if (yyout == NULL) return S_INIT; fwrite( yytext, yyleng, 1, yyout );}
%}

delim   [ \t]
ws      {delim}+
letter  [A-Za-z]
letter_ ({letter}|\-|_)
digit   [0-9]
number  [1-9]{digit}+
cmd     {letter}+
path    [a-z0-9\-_]+
literal {letter_}({letter_}|{digit})*

%s COMMAND
%s DEFINE
%s ARGUMENT
%s ARGUMENT1
%s ARGUMENT_N
%s ARGUMENT_F
%s ARGUMENT_END
%s STRING

%%

{ws}        {if (YY_START == INITIAL && yyout) ECHO;}
\\\n        {++yylineno;}
\n          {
    BEGIN INITIAL;
    ++yylineno;
    if (YY_START == INITIAL) {
        if (yyout) fputc('\n', yyout);
    } else if (YY_START != ARGUMENT_END) {
        yyterminate();
    }
}
<INITIAL>##         {BEGIN COMMAND;}
<COMMAND>version    {BEGIN ARGUMENT_N; return(S_VER);}
<COMMAND>pragma     {BEGIN ARGUMENT; return(S_PRAGMA);}
<COMMAND>package    {BEGIN ARGUMENT; return(S_PACK);}
<COMMAND>enter      {BEGIN ARGUMENT_F; return(S_ENTER);}
<COMMAND>exit       {BEGIN ARGUMENT_F; return(S_EXIT);}
<COMMAND>file       {BEGIN ARGUMENT_F; return(S_FILE);}
<COMMAND>function   {BEGIN ARGUMENT_F; return(S_FUNC);}
<COMMAND>tag        {BEGIN ARGUMENT_F; return(S_TAG);}
<COMMAND>{cmd}      {BEGIN ARGUMENT; return(CMD);}

<ARGUMENT>\(        {BEGIN ARGUMENT1; return(SLP);}
<ARGUMENT1>\)       {BEGIN ARGUMENT; return(SRP);}

<ARGUMENT1>\"       {BEGIN STRING;}
<STRING>\"          {BEGIN ARGUMENT1;}
<STRING>([^\"\n]|\\\"|\\\n)*    {return(STR);}

<ARGUMENT1>on       {return(ON);}
<ARGUMENT1>off      {return(OFF);}
<ARGUMENT1>":"      {return(CLN);}
<ARGUMENT1>\,       {return(CMA);}

<ARGUMENT_F>{path}  {return(PATH);}
<ARGUMENT_N,ARGUMENT1>{number}  {return(NUM);}
<ARGUMENT,ARGUMENT1>{literal}   {return(LITERAL);}
<<EOF>>             {return(EOF);}

%%

char* bytes_copy(char* src, int len) {
	char* buffer = (char*)malloc((len + 1) * sizeof(char));
    if (buffer == NULL) return NULL;

	strncpy(buffer, src, len);
	buffer[len] = '\0';
	return buffer;
}

Token* get_token(enum TokenSyn syn) {
    Token* token = (Token*)malloc(sizeof(Token));
    if (token == NULL) return NULL;

    if (syn == NUM) {
        int i = atoi(yytext);
        token->val = &i;
    } else {
        token->val = bytes_copy(yytext, yyleng);
        if (token->val == NULL) {
            free(token);
            return NULL;
        }
    }
    return token;
}