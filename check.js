const fs = require('fs');
const parser = require('@babel/parser');

try {
    const code = fs.readFileSync('b:\\ASTRAgram-main\\backend-java\\src\\main\\resources\\static\\app.js', 'utf8');
    parser.parse(code, {
        sourceType: 'module',
        plugins: ['jsx']
    });
    console.log("Syntax is perfectly fine!");
} catch (e) {
    console.error(e.message);
}
