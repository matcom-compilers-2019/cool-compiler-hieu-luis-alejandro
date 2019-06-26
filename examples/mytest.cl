class A {
  x : String;
  x() : String { x };
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
      out_string("False");
      let x : A <- new A in
        if isvoid x.x()
        then out_string(x.x())
        else out_string("False")
        fi;
    }
  };
};
