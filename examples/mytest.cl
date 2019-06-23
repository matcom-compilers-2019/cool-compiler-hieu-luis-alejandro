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

   fibo (n : Int) : Int {
      {
         if n <= 0
         then 0
         else fibo(n-1) + n
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
   main() : SELF_TYPE {
      let x : B <- new B, a : Int in {
         a <- in_int();
         out_int(x@A.method5(a));
      };
   };
};