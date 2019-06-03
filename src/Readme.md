# Cool Compiler

## Gramatica

```
Rule 0     S -> program
Rule 1     program -> class_list
Rule 2     class_list -> class_list class SEMICOLON
Rule 3     class_list -> class SEMICOLON
Rule 4     class -> CLASS TYPE LBRACE features_list_opt RBRACE
Rule 5     class -> CLASS TYPE INHERITS TYPE LBRACE features_list_opt RBRACE
Rule 6     features_list_opt -> features_list
Rule 7     features_list_opt -> empty
Rule 8     features_list -> features_list feature SEMICOLON
Rule 9     features_list -> feature SEMICOLON
Rule 10    feature -> ID LPAREN formal_params_list RPAREN COLON TYPE LBRACE expression RBRACE
Rule 11    feature -> ID LPAREN RPAREN COLON TYPE LBRACE expression RBRACE
Rule 12    feature -> ID COLON TYPE ASSIGN expression
Rule 13    feature -> ID COLON TYPE
Rule 14    formal_params_list -> formal_params_list COMMA formal_param
Rule 15    formal_params_list -> formal_param
Rule 16    formal_param -> ID COLON TYPE
Rule 17    expression -> ID
Rule 18    expression -> INTEGER
Rule 19    expression -> BOOLEAN
Rule 20    expression -> STRING
Rule 21    expression -> SELF
Rule 22    expression -> LBRACE block_list RBRACE
Rule 23    block_list -> block_list expression SEMICOLON
Rule 24    block_list -> expression SEMICOLON
Rule 25    expression -> ID ASSIGN expression
Rule 26    expression -> expression DOT ID LPAREN arguments_list_opt RPAREN
Rule 27    arguments_list_opt -> arguments_list
Rule 28    arguments_list_opt -> empty
Rule 29    arguments_list -> arguments_list COMMA expression
Rule 30    arguments_list -> expression
Rule 31    expression -> expression AT TYPE DOT ID LPAREN arguments_list_opt RPAREN
Rule 32    expression -> ID LPAREN arguments_list_opt RPAREN
Rule 33    expression -> expression PLUS expression
Rule 34    expression -> expression MINUS expression
Rule 35    expression -> expression MULTIPLY expression
Rule 36    expression -> expression DIVIDE expression
Rule 37    expression -> expression LT expression
Rule 38    expression -> expression LTEQ expression
Rule 39    expression -> expression EQ expression
Rule 40    expression -> LPAREN expression RPAREN
Rule 41    expression -> IF expression THEN expression ELSE expression FI
Rule 42    expression -> WHILE expression LOOP expression POOL
Rule 43    expression -> let_expression
Rule 44    let_expression -> LET ID COLON TYPE IN expression
Rule 45    let_expression -> nested_lets COMMA LET ID COLON TYPE
Rule 46    let_expression -> LET ID COLON TYPE ASSIGN expression IN expression
Rule 47    let_expression -> nested_lets COMMA LET ID COLON TYPE ASSIGN expression
Rule 48    nested_lets -> ID COLON TYPE IN expression
Rule 49    nested_lets -> nested_lets COMMA ID COLON TYPE
Rule 50    nested_lets -> ID COLON TYPE ASSIGN expression IN expression
Rule 51    nested_lets -> nested_lets COMMA ID COLON TYPE ASSIGN expression
Rule 52    expression -> CASE expression OF actions_list ESAC
Rule 53    actions_list -> actions_list action
Rule 54    actions_list -> action
Rule 55    action -> ID COLON TYPE ARROW expression SEMICOLON
Rule 56    expression -> NEW TYPE
Rule 57    expression -> ISVOID expression
Rule 58    expression -> INT_COMP expression
Rule 59    expression -> NOT expression
Rule 60    empty -> <empty>
```

## Intrucciones

Incluya en esta carpeta **todo** el código fuente que es necesario para compilar y/o ejecutar su compilador desde cero.

**No incluya** archivos generados automáticamente, tales como binarios (e.g, `.exe`, `.pyc`), archivos auxiliares o archivos de logs, reportes, etc.

## Compilando su proyecto

Si es necesario compilar su proyecto, incluya todas las instrucciones necesarias en el archivo [`/src/makefile`](/src/makefile) que está en esta misma carpeta.
Durante la evaluación su proyecto se compilará ejecutando la siguiente secuencia:

```bash
$ cd source
$ make clean
$ make
```

## Ejecutando su proyecto

Incluya en el archivo [`/src/coolc.sh`](/src/compile.sh) todas las instrucciones que hacen falta para lanzar su compilador. Recibirá como entrada un archivo con extensión `.cl` y debe generar como salida un archivo `.mips` cuyo nombre será el mismo que la entrada.

Para lanzar el compilador, se ejecutará la siguiente instrucción:

```bash
$ cd source
$ ./compile.sh <input_file.cl>
```

> **NOTA:** Su proyecto será ejecutado y evaluado en un entorno **Linux**. Si usted desarrolló en un entorno diferente, asegúrese de que es posible ejecutar su proyecto en Linux. En el caso de **.NET**, vea las instrucciones para portar su proyecto a **.NET Core** (la versión Open Source) [aquí](https://dotnet.microsoft.com/) y asegúrese de probar que funciona en Linux. **NO es posible** entregar su proyecto en forma de una solución que necesite abrirse con Visual Studio para funcionar.

## Sobre el lenguaje COOL

Ud. podrá encontrar la especificación formal del lenguaje COOL en el documento [_COOL Language Reference Manual_](../doc/cool-manual.pdf), que se distribuye junto con el presente texto.

## Sobre el funcionamiento del compilador

El compilador de COOL se ejecutará como se ha definido anteriormente.
En caso de que no ocurran errores durante la operación del compilador, **coolc.sh** deberá terminar con código de salida 0, generar (o sobrescribir si ya existe) en la misma carpeta del archivo **.cl** procesado, y con el mismo nombre que éste, un archivo con extension **.mips** que pueda ser ejecutado con **spim**. Además, reportar a la salida estándar solamente lo siguiente:

    <línea_con_nombre_y_versión_del_compilador>
    <línea_con_copyright_para_el_compilador>

En caso de que ocurran errores durante la operación del compilador, **coolc.sh** deberá terminar con código
de salida (exit code) 1 y reportar a la salida estándar (standard output stream) lo que sigue...

    <línea_con_nombre_y_versión_del_compilador>
    <línea_con_copyright_para_el_compilador>
    <línea_de_error>_1
    ...
    <línea_de_error>_n

... donde `<línea_de_error>_i` tiene el siguiente formato:

    (<línea>,<columna>) - <tipo_de_error>: <texto_del_error>

Los campos `<línea>` y `<columna>` indican la ubicación del error en el fichero **.cl** procesado. En caso
de que la naturaleza del error sea tal que no pueda asociárselo a una línea y columna en el archivo de
código fuente, el valor de dichos campos debe ser 0.

El campo `<tipo_de_error>` será alguno entre:

- `CompilerError`: se reporta al detectar alguna anomalía con la entrada del compilador. Por ejemplo, si el fichero a compilar no existe.
- `LexicographicError`: errores detectados por el lexer.
- `SyntacticError`: errores detectados por el parser.
- `NameError`: se reporta al referenciar un `identificador` en un ámbito en el que no es visible.
- `TypeError`: se reporta al detectar un problema de tipos. Incluye:
    - incompatibilidad de tipos entre `rvalue` y `lvalue`,
    - operación no definida entre objetos de ciertos tipos, y
    - tipo referenciado pero no definido.
- `AttributeError`: se reporta cuando un atributo o método se referencia pero no está definido.
- `SemanticError`: cualquier otro error semántico.

## Sobre la Implementación del Compilador de COOL

Para la implementación del compilador Ud. debe utilizar una herramienta generadora de analizadores
lexicográficos y sintácticos. Puede utilizar la que sea de su preferencia.
