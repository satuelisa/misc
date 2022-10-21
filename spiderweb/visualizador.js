
var AXISLEN = 320;
var TEXTSEP = 50;
var MIDPT = 400;
var COLORS = {"0": "#7b241c" , "25": "#a04000", "50": "#f1c40f", "75": "#1e8449", "100": "#2471a3", "hl": "#ff00ff"};
var quartiles = {};
var results = {};
var selected = null;

var maxpts = {
    "ej19": [8, 4, 8],    
    "ad18": [8, 4, 8],
    "ej18": [8, 6, 6], 
    "ad17": [6, 5, 9], 
    "ej17": [5, 3, 4, 4, 4], 
    "ad16": [5, 3, 5, 4, 3], 
    "ej16": [7, 10, 3], 
    "ad15": [5, 4, 4, 3, 4]};
var sel = document.getElementById('semester');
var longsem = {"ad": "Agosto-diciembre", "ej": "Enero-junio"}
var active = null; 


function loadList(){
    selected = null; // reset
    var request = new XMLHttpRequest();
    request.open('GET', 'https://elisa.dyndns-web.com/teaching/mat/discretas/resultados/' + active + '.lst', true);
    request.send(null);
    request.onreadystatechange = function () {
	if (request.readyState === 4 && request.status === 200) {
	    document.getElementById("listing").innerHTML = "<p>Participante:</p> <select id='students' onchange='highlight()' size='10'></select>";
	    var st = document.getElementById("students");
	    var lst = request.responseText.split("\n"); // list of participants
	    var questions = {};
	    results = {}; // reset
	    for (var i = 0; i < lst.length; i++) {
		var content = lst[i].trim();
		if (content.length > 7) {
		    var data = content.split(" "); // data for each participant
		    var option = document.createElement("option");
		    for (var j = 1; j < data.length; j++) {
			questions[j] += (" " + data[j]);
		    }
		    var pid = data.splice(0, 1); // ID of each participant
		    option.text = pid;
		    results[pid] = data;		    
		    st.add(option);
		}
	    }
	    quartiles = {}; // reset
	    var n = maxpts[active].length; // number of regular questions
	    for (var i = 1; i <= n; i++) {
		var data = questions[i].split(" ");
		var values = [];
		for (var j = 1; j < data.length; j++) { // the first one is always undefined
		    if (data[j] === "NA") {
			values.push(0);
		    } else {
			values.push(parseFloat(data[j]));
		    }
		}
		values.sort();
		var k = values.length;
		quartiles[i] = {"0": values[0], "25": values[Math.floor(k / 4)], "50": values[Math.floor(k / 2)], "75": values[Math.floor(3 * k / 4)], "100": values[k - 1]};
	    }
	    redraw();
	}
    }
}

for (var sem in maxpts) {
    if (maxpts.hasOwnProperty(sem)) {
	if (active === null) { 
	    active = sem; // display the first one
	}
	var opt = document.createElement('option');
	opt.value = sem;
	opt.innerHTML = longsem[sem.substring(0, 2)] + ' 20' + sem.substring(2, 4);
	sel.appendChild(opt);
    }
}
function semester() {
    active = document.getElementById("semester").options[document.getElementById("semester").selectedIndex].value;
    loadList();
}
semester(active);

function redraw() {
    var c = document.getElementById("draw");
    var ctx = c.getContext("2d");
    ctx.clearRect(0, 0, c.width, c.height);
    var n = maxpts[active].length; // number of regular questions    
    var increment = 2 * Math.PI / n;
    for (var qua = 100; qua >= 0; qua -= 25) { // quartiles
	ctx.fillStyle = COLORS[qua];
	ctx.beginPath();
	for (var i = 0; i < n; i++) {		    
	    var angle = i * increment;
	    var maximum = maxpts[active][i];
	    var value = quartiles[i + 1][qua];
	    var dist = (value / maximum) * AXISLEN;
	    var x = MIDPT + Math.cos(angle) * dist;
	    var y = MIDPT + Math.sin(angle) * dist;
	    if (i == 0) { 
		ctx.moveTo(x, y);
	    } else { 
		ctx.lineTo(x, y);
	    }
	}
	ctx.closePath();
	ctx.fill();
    }
    ctx.font="15px Verdana";
    for (var i = 0; i < n; i++) { // axis on top
	var angle = i * increment;
	ctx.beginPath();
	ctx.moveTo(MIDPT, MIDPT);
	var x = MIDPT + Math.cos(angle) * AXISLEN;
	var y = MIDPT + Math.sin(angle) * AXISLEN;
	ctx.strokeStyle = '#000000';
	ctx.lineWidth = 3;
	ctx.lineTo(x, y);
	ctx.stroke();
	var tx = MIDPT + Math.cos(angle) * (AXISLEN + TEXTSEP);
	var ty = MIDPT + Math.sin(angle) * (AXISLEN + TEXTSEP);
	ctx.fillStyle = "#000000";
	ctx.fillText("P" + (i + 1) + " (" + maxpts[active][i] + " pts)", tx, ty);	
    }
    if (selected === null) {
	return; // nothing more to draw
    }
    ctx.strokeStyle = COLORS["hl"];
    ctx.lineWidth = 5;
    ctx.beginPath();
    var fields = results[selected];
    for (var i = 0; i < n; i++) {
	var angle = i * increment;
	var value = 0;
	if (!(fields[i] === "NA")) {
	    value = parseFloat(fields[i]);
	}
	var maximum = maxpts[active][i];
	var dist = (value / maximum) * AXISLEN;
	var x = MIDPT + Math.cos(angle) * dist;
	var y = MIDPT + Math.sin(angle) * dist;
	if (i == 0) { 
	    ctx.moveTo(x, y);
	} else {
	    ctx.lineTo(x, y);	    
	} 
    }
    ctx.closePath();
    ctx.stroke();
}

function highlight() {
    selected = document.getElementById("students").options[document.getElementById("students").selectedIndex].value;
    redraw();
}

