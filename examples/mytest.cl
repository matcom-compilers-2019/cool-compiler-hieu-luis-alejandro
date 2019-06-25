class A {

};

class C inherits A {

};

class B inherits A {  -- B is a number squared
};

class Main inherits IO {
  main() : Object
  {
     let var : C <- new C in
      case var of
         a : A => out_string("Class type is now A\n");
         b : B => out_string("Class type is now B\n");
         c : C => out_string("Class type is now C\n");
         o : Object => out_string("Oooops\n");
      esac
  };
};
