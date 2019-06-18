class A {
    v1 : SELF_TYPE <- new A;
    f(p1: Int): SELF_TYPE {
        new A;
    };
};

class B inherits A {
    var : B;
    g(): B {
        var <- f(0);
        var <- v1;
    };
};