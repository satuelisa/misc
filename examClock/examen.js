var men = parseParameter("msg");
if (men != null) {
    document.getElementById("mensaje").innerHTML = "<em>" + men + "</em>";
}


var inicio = parseParameter("ini");
var dur = parseParameter("dur");
var f = null;
if (inicio != null && dur != null) {
    var st = new Date();
    var fi = new Date();
    var t = inicio.split(":");
    var h = parseInt(t[0]);
    var m = parseInt(t[1]);
    st.setHours(h, m, 0);
    var d = parseInt(dur);
    while (d >= 60) {
        h++;
        d -= 60;
    }
    if (m + d == 60) {
        h++;
        d -= 60;
    }
    m += d;
    fi.setHours(h, m, 0);
    document.getElementById("final").innerHTML =
        "El examen termina a las " + h + ":" + prep(m) + " hrs.";
}

function parseParameter(val) {
    var result = null;
    tmp = [];
    var items = location.search.substr(1).split("&");
    for (var index = 0; index < items.length; index++) {
        tmp = items[index].split("=");
        if (tmp[0] === val) result = decodeURIComponent(tmp[1]);
    }
    return result;
}

function prep(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10                                                               
    return i;
}

function timer() {
    var now = new Date();
    var h = now.getHours();
    var m = now.getMinutes();
    document.getElementById("reloj").innerHTML =
        "Son las " + h + ":" + prep(m) + " hrs.";
    if (fi != null) {
        var q = Math.round((fi - now) / 1000 / 60);
        var h = 0;
        while (q >= 60) {
            h++;
            q -= 60;
        }
        var plural = '';
        var horas = '';
        if (h > 0) {
            horas = h + ' hora';
            if (h > 1) {
                horas += 's';
                plural = 'n';
            }
        }
        var minutos = '';
        if (q > 0) {
            minutos = q + ' minuto';
            if (q > 1) {
                minutos += 's';
                plural = 'n';
            }
        }
        var conectivo = '';
        if (h > 0 && q > 0) {
            conectivo = ' y ';
        }
        document.getElementById("quedan").innerHTML =
            'Queda' + plural + ' ' + horas + conectivo + minutos + '.';
    }
    var t = setTimeout(timer, 6000);
}
