var sem = document.getElementById("semaforo");
sem.style.background = 'black';
var c = sem.getContext("2d");
var w = sem.width;
var h = sem.height;
var fs = h / 5;
var student = "";
var socket = null;
var ready = false;
var rc = null;
var yc = null;
var gc = null;

var green = true;
var yellow = false;
var red = false;


function getCookieByName(name) {
    var cookiestring=RegExp(""+name+"[^;]+").exec(document.cookie);
    return unescape(!!cookiestring ? cookiestring.toString().replace(/^[^=]+./,"") : "");
}

function connect() {
    socket = new WebSocket("ws://148.234.195.15:8080/chat?student=" + student);
    socket.onopen = function() {
	ready = true;
	document.getElementById("nick").innerHTML = student + ": ";
	if (green) {
	    socket.send("g\n");
	} else if (yellow) {
	    socket.send("y\n");
	} else if (red) {
	    socket.send("r\n");
	}
    };
    socket.onmessage = function(evt) { 
	var msg = evt.data;
	if (msg.indexOf('[') >= 0) {
	    append(msg);
	} else {
	    var tokens = msg.split(" ");
	    rc = parseInt(tokens[0]);
	    yc = parseInt(tokens[1]);
	    gc = parseInt(tokens[2]);
	    dibuja();
	}
    }; 
    socket.onclose = function() { 
	ready = false;
	rc = null;
	yc = null;
	gc = null;
	socket = null;
    };
}

function login() {
    if (!("WebSocket" in window)) {
	chat.innerHTML = "Tu navegador web no sabe hacer esto. Cambia a Chrome.";
    } else if (socket == null) {
        student = prompt("Pon tu nombre para acceder el chat.");
        if (student != null && student != "") {
          document.cookie = "student=" + student;
            document.cookie += "; expires=Thu, 01 Jan 1970 00:00:01 GMT;";
            document.getElementById("login").innerHTML = 
		"<em>Sesi&oacute;n activada para " 
		+ student + "</em>." 
		+ "<p><button onclick=\"logout()\">Logout</button></p>"
            connect();
	}
    }
}

function logout() {
    student = "";
    rc = null;
    yc = null;
    gc = null;
    if (socket != null) {
	socket.close();
    }
    socket = null;
    document.getElementById("chat").innerHTML = "<span style=\"color:yellow\">Desconectado.</span><br>";
    document.cookie = "student=; expires=Thu, 01 Jan 1970 00:00:01 GMT;";
    document.getElementById("login").innerHTML = 
       "<p><button onclick=\"login()\">Login</button></p>"
    dibuja();
}

  function append(msg) {
      var target =  document.getElementById("chat");
      target.innerHTML += "<p>" + msg + "</p>";
      target.scrollTop = target.scrollHeight;
  }

function message() {
    var content = document.getElementById("msg").value;
     if (content != "") {
	 var target =  document.getElementById("chat");
	 target.innerHTML += "<span style=\"color:DeepSkyBlue\">T&uacute;: " + content + "</span><br>";
       target.scrollTop = target.scrollHeight;
	 msg.value = "";
	 socket.send("[" + student + "]: " + content + "\n");
     }  
  }

var prop = 1.0 * w / h;
var low = 30;
var high = 96;
var step = w / 6;
var rx = step;
var yx = 3 * step;
var gx = 5 * step;
var ay = h / 4;
var ar = 4 * step / 5;

function limites(valor, minimo, maximo) {
  if (valor < minimo) {
      return minimo;
  } else if (valor > maximo) {
      return  maximo;
  } else {
      return valor;
  }
}

function cambio(delta) {
    h = limites(h + delta, 20, 500);
    w = prop * h;
    c.canvas.width  = w;
    c.canvas.height = h;
    step = w / 6;
    rx = step;
    yx = 3 * step;
    gx = 5 * step;
    ay = h / 4;
    ar = 4 * step / 5;
    if (delta > 0) {
	fs++;
    } else {
	fs--;
    }
    dibuja();
}

function dibuja() {
    c.clearRect(0, 0, w, h);
    c.font = fs + "px Georgia";
    redLight();
    yellowLight();
    greenLight();
}

function text(counter, x) {
    if (counter != null && counter > 0) {
	c.fillStyle = 'rgb(255, 255, 255)';
	c.fillText("" + counter, x, 3 * ay);
    }
}

function light(x, flag, on, off) {
    c.beginPath();
    c.arc(x, ay, ar, 0, 2*Math.PI);
    if (flag) { 
	c.fillStyle = on;
    } else {
	c.fillStyle = off;
    }
    c.fill();
    c.stroke();
}

function color(r, g, b) {
    return 'rgb(' + r + ', ' + g + ', ' + b + ')';
}

function redLight() {
    light(rx, red, color(255, low, low), color(high, 0, 0));
    text(rc, rx);
}

function yellowLight() {
    light(yx, yellow, color(255, 255, low), color(high, high, 0));
    text(yc, yx);
}

function greenLight() {
    light(gx, green, color(low, 255, low), color(0, high, 0));
    text(gc, gx);
}

dibuja();

function inside(cx, ex, ey) {
    var dx = cx - ex;
    var dy = ay - ey;
//    document.getElementById("debug").innerHTML += dy + "<br>";
    return Math.sqrt(dx * dx + dy * dy) < 2 * ar;
}

sem.addEventListener('click', function(event) {
    var x = event.pageX;
    var y = event.pageY;
    if (inside(gx, x, y)) {
	green = true; 
	yellow = red = false;
	if (ready) {
	    socket.send("g\n");
	}
    } else if (inside(yx, x, y)) {
	yellow = true;
	green = red = false;
	if (ready) {
	    socket.send("y\n");
	}
    } else if (inside(rx, x, y)) {
	red = true;
	yellow = green = false;
	if (ready) {
	    socket.send("r\n");
	}
    } 
    dibuja();
}, false);

