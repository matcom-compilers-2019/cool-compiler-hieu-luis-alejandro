class A {
  x : C;
  x() : C { x };
  w() : Int { 10 };
};

class C inherits A {

};

class B inherits A{  -- B is a number squared
  v : A <- new A;
  s() : Int { 1 };

};

class Main inherits IO {

  main() : Object
  {
    {
      let x : A <- new A in
        if isvoid x.x()
        then out_string("True")
        else out_string("False")
        fi;
    }
  };
};
