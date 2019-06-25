class A {

   var : Int <- 0;

   value() : Int { var };
   
   method5(num : Int) : Int {  -- factorial
      let x : Int <- 1 in
      {
         (let y : Int <- 1 in
            while y <= num loop
               {
                  x <- x * y;
                  y <- y + 1;
               }
            pool
         );
         x;
      }
   };

};

class B inherits A {  -- B is a number squared

   method5(num : Int) : Int { -- square
      (let x : Int in
	 {
            x <- num * num;
	 }
      )
   };

   method3 (n : Int) : String {
      if n < 10 
      then "True"
      else "False"
      fi;
   };

   fibo (a : A, b : B) : String {
      {
         if a == b
         then "True"
         else "False"
         fi;
      }
   };
   
   -- method6 (n:Bool) : Bool {
   --   let a : Object in {
   --      a <- 2@Int.abort();
   --      n <- method3(true);
   --   };
   -- };
};

class Main inherits IO {
   method( var : String ) : Object
   {
      let var : String <- "good" in
      out_string( var )
   };

  main() : Object
  {
      let x : String in {
         x <- in_string();
         out_int(x.length());
         out_string("\n".concat(x.substr(0,5)));
      }
  };
};
