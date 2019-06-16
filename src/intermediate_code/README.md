# CIL Visitor Output
SetAttr: attribute : Integer,   src : Integer / String
GetAttr: attribute : Integer
Minus: left: Integer/String

Hacer Allocate Void devuelve siempre el mismo puntero a una direccion de memoria con valor 0
Allocate recibe un string que es el nombre del tipo

El atributo en el offset 0 de Int, Bool es el valor
El atributo en el offset 1 de String es la referencia a la cadena

El valor devuelto por TypeOf debe ser algo que pueda pasarse a Vcall