// Datei: app.js
document.getElementById('run-button').addEventListener('click', function() {
    var code = document.getElementById('code-editor').value;
    var output = '';

    // Skulpt-Konfiguration
    Sk.configure({
        output: function(text) {
            output += text;
        },
        read: function(x) {
            if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
                throw "File not found: '" + x + "'";
            return Sk.builtinFiles["files"][x];
        }
    });

    // Python-Code mit Skulpt ausführen
    var myPromise = Sk.misceval.asyncToPromise(function() {
        return Sk.importMainWithBody("<stdin>", false, code, true);
    });

    myPromise.then(function(mod) {
        document.getElementById('output-console').innerText = output;
    },
    function(err) {
        document.getElementById('output-console').innerText = err.toString();
    });
});
