(*
 *  A contribution from Anne Sheets (sheets@cory)
 *
 *  Tests the arithmetic operations and various other things
 *)

class A {

   var : Int <- 0;

   value() : Int { var };

   set_var(num : Int) : SELF_TYPE {
      {
         var <- num;
         self;
      }
   };

   method3(num : Int) : C {  -- negate
      (let x : Int <- 1, y : Int <- 2 in
	 {
            y;
	 }
      )
   };
};