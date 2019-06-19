class A {
    v1 : SELF_TYPE <- self;
    f(p1: Int): SELF_TYPE {
        new A;
    };
};

class B inherits A {
    var : D;
    f(p1:Int): SELF_TYPE {
        self;
    };
    g(): B {
        {
            --var <- f(0);
            var <- new D@B.f(0);
        }
    };
};

class C inherits B {};

class D inherits C {};