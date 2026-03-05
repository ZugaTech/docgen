class JSSample {
    undocumentedMethod(x, y) {
        console.log(x, y);
    }

    /** JSDoc is here */
    documentedMethod() {
        return true;
    }
}

function undocumentedFunction(a, b) {
    console.log(a, b);
}

/** Has JSDoc */
function documentedFunction() {
    pass;
}

const arrowFunc = (z) => {
    return z * 2;
};
