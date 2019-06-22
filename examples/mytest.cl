class A {

   var : Int <- 0;

   value() : Int { var };

   set_var(num : Int) : SELF_TYPE {
      {
         var <- num;
         self;
      }
   };

   method1(num : Int) : SELF_TYPE {  -- same
      self
   };

   method2(num1 : Int, num2 : Int) : Int {  -- plus
      (let x : Int in
	 {
            x <- num1 + num2;
	 }
      )
   };

   method5(num : Int) : Int {  -- factorial
      (let x : Int <- 1 in
	 {
	    (let y : Int <- 1 in
	       while y <= num loop
	          {
                     x <- x * y;
	             y <- y + 1;
	          }
	       pool
	    );
       1;
	 }
      )
   };

};

class B  {  -- B is a number squared

   method5(num : Int) : Int { -- square
      (let x : Int in
	 {
            x <- num * num;
	 }
      )
   };

   method3 (n:Bool) : Bool {
      n <- "asda" == "s";
   };

   
   method6 (n:Bool) : Bool {
      let a : Object in {
         a <- 2@Int.abort();
         n <- method3(true);
      };
   };
};

class Main {
   main() : {
      
   }
};