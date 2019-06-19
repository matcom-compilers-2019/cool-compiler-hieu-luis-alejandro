class A {
    v1 : SELF_TYPE <- self;
    f(p1: Int): SELF_TYPE {
        new A;
    };
};

class B inherits A {
    var : B;
    f(p1:Int): SELF_TYPE {
        self;
    };
    g(): B {
        {
            var <- f(0);
            var <- self@A.f(0);
        }
    };
};