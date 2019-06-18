# CIL Visitor Output
SetAttr: attribute : Integer,   src : Integer / String
GetAttr: attribute : Integer
Minus: left: Integer/String

Hacer Allocate Void devuelve siempre el mismo puntero a una direccion de memoria con valor 0
Allocate recibe un string que es el nombre del tipo

El atributo en el offset 0 de Int, Bool es el valor
El atributo en el offset 1 de String es la referencia a la cadena

El valor devuelto por TypeOf debe ser algo que pueda pasarse a Vcall

Call recibe el nombre del metodo en forma de {clase}_{metodo}

Equal (src, first, second) compara dos variables que son referencias a objetos

PushParam y PopParam puede recibir un string, en ese caso el string representa un tipo y se reemplaza por su valor equivalente en la fase de MIPS

En mips debe existir una funcion con nombre CONFORMS_FUNC (src/commons/settings.py), que devuelva, dado 2 tipos, True si el primero conforma el segundo y False en caso contrario.