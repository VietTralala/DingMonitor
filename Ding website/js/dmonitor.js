// JavaScript Document

var timer;
var timing;

function allStopsSelect () {
	$.post("/php/phpsqlajax_genxml_dmonitor.php?src=stopsa", function(data) {
        var xml = data;
		var stops = xml.documentElement.getElementsByTagName("stop");
		for (var i = 0; i < stops.length; i++) {
			var name = stops[i].getAttribute("name");
			var haltepunkt = stops[i].getAttribute("haltepunkt");
			var lat = parseFloat(stops[i].getAttribute("lat"));
			var lng = parseFloat(stops[i].getAttribute("lng"));
			
			var selectStop = document.createElement('option');
			selectStop.className = "styled-option"; 
			selectStop.innerHTML = name + ' (' + haltepunkt + ')';
			selectStop.value = name + ' (' + haltepunkt + ')';
			
		//	document.getElementById('Haltestellenliste').appendChild(selectStop);
			if (document.getElementById('HaltestellenlisteSelect')) {
				document.getElementById('HaltestellenlisteSelect').appendChild(selectStop);
			}
		}		
	
	document.getElementById('Haltestelle').addEventListener('focus', function() {
	document.getElementById('Haltestelle').value ="";
	stopTimer();
	});
	
	/*document.getElementById('HaltestellenlisteSelect').addEventListener('change', function() {
	var dm_nummer = document.getElementById('HaltestellenlisteSelect').this.value;
	getStopDM(dm_nummer);
	});*/
		
	document.getElementById('Button_Haltestelle').addEventListener('click', function() {
	var dm_nummer;
	dm_nummer = document.getElementById('Haltestelle').value;
	
	if (dm_nummer !== '') {
		getStopDM(dm_nummer);
	}
	else {
	dm_nummer = document.getElementById('HaltestellenlisteSelect').value;
		getStopDM(dm_nummer);
	}
	});
});
}

function getStopDM (dm_send) {
	if (dm_send.length > 4) {
	var haltepunkt = dm_send.substr(-5, 4);
	}
	else {
		var haltepunkt = dm_send;
	}
	dm_timer = haltepunkt;
	//console.log(haltepunkt);
	getXML("//www.ding.eu/ding3/XSLT_DM_REQUEST?sessionID=0&type_dm=stopID&name_dm=900" + haltepunkt + "&useRealtime=1&excludedMeans=0&excludedMeans=6&excludedMeans=10&outputFormat=XML", function(data) {
////www.ding.eu/ding3/XSLT_DM_REQUEST?sessionID=0&type_dm=stopID&name_dm=900" + haltepunkt + "&outputFormat=XML&useRealtime=1
		var xml = data.responseXML;
		var session = xml.documentElement.getAttribute("sessionID");
		var request = xml.getElementsByTagName("itdDepartureMonitorRequest").item(0).getAttribute("requestID");
			getXML("//www.ding.eu/ding3/XSLT_DM_REQUEST?useRealtime=1&sessionID=" + session + "&requestID=" + request + "&dmLineSelectionAll=1&limit=50&outputFormat=XML", function(data) {
////www.ding.eu/ding3/XSLT_DM_REQUEST?useRealtime=1&sessionID=" + session + "&requestID=" + request + "&dmLineSelectionAll=1
		
		var xml = data.responseXML;
		var list = xml.getElementsByTagName("itdDeparture");
		var dmMonitor = [];
		var anzeige = '';
		document.getElementById('abfahrtsmonitorTableBody').innerHTML = '';
		for (i=0; i<list.length; i++) {			
			var itdServingLine = list.item(i).getElementsByTagName("itdServingLine");
			var direction = itdServingLine.item(0).getAttribute("direction");
			var linie = itdServingLine.item(0).getAttribute("number");
			var typ = itdServingLine.item(0).getAttribute("motType");
			var realtime = itdServingLine.item(0).getAttribute("realtime");
			var departure = (list.item(i).getAttribute("countdown") - 1);
			var platform = list.item(i).getAttribute("platformName");
			var itdNoTrain = list.item(i).getElementsByTagName("itdNoTrain");
			var delay = itdNoTrain.item(0).getAttribute("delay");
			var itdRouteDescText = itdServingLine.item(0).getElementsByTagName("itdRouteDescText");
			var routeText = itdRouteDescText.item(0).innerHTML;
			
			
			//if ((linie <= 19 || linie.match('N') || linie == "E"))  {
			if ((realtime == 1) && (linie <= 16 || linie.match('N') || linie == "E"))  {
				var xmlArray = [linie, direction, parseInt(departure), parseInt(typ), routeText];
				dmMonitor.push(xmlArray);
				xmlArray = '';
			}
		}
		// nach countdown sortieren
		dmMonitor.sort((function(index){
    	return function(a, b){
        return (a[index] === b[index] ? 0 : (a[index] < b[index] ? -1 : 1));
    	};
		})(2));
		
		if (dmMonitor.length > 15) {
			var ende = 15;
		}
		else {
			var ende = dmMonitor.length;
		}		

		//var xmlArray = [linie, direction, parseInt(departure), parseInt(typ), routeText];

		for (i=0; i<ende; i++) {
		anzeige += '<td><img src="/img/Linie_' + dmMonitor[i][0] + '_Pikto.gif" class="imgLinie" alt="Linie ' + dmMonitor[i][0] + '"></td><td>' + dmMonitor[i][1] + '</td>';
				if ((dmMonitor[i][2] <= 1) && (dmMonitor[i][2] > 0) && (dmMonitor[i][3] == 5)) {
						anzeige += '<td><img src="/img/dmBus.png" class="linieDM" alt="jetzt"></td></tr>';
				}
				else if ((dmMonitor[i][2] <= 1) && (dmMonitor[i][2] > 0) && (dmMonitor[i][3] == 4)) {
					anzeige += '<td><img src="/img/dmStrab.png" class="linieDM" alt="jetzt"></td></tr>';
				}
				else if ((dmMonitor[i][2] <= 0) && (dmMonitor[i][3] == 5)) {
						anzeige += '<td><span class="blink"><img src="/img/dmBus.png" class="linieDM" alt="jetzt"></span></td></tr>';
				}
				else if ((dmMonitor[i][2] <= 0) && (dmMonitor[i][3] == 4)) {
					anzeige += '<td><span class="blink"><img src="/img/dmStrab.png" class="linieDM" alt="jetzt"></span></td></tr>';
				}
				else {
					anzeige += '<td>in ' + dmMonitor[i][2] + ' Min.</td></tr>';		
				}
			}
				
		if (anzeige.length == 0) {
		anzeige = '<tr><td colspan="3">zur Zeit liegen keine Echtzeitdaten vor</td></tr>';
		}
				
		var odvNameElem = xml.getElementsByTagName("odvNameElem");
		var dm_name = odvNameElem.item(0).textContent;	
			if (dm_name.match('900')) {
				document.getElementById('colhead').innerHTML = '';
				document.getElementById('dm_name').innerHTML = 'Es konnte keine Haltestelle gefunden werden';
				document.getElementById('abfahrtsmonitorTableBody').innerHTML = '<tr><td colspan="3">Bitte geben Sie die Anfangsbuchstaben der Haltestelle ein und wählen Sie diese dann aus der Liste aus.</td></tr>';
			}
			else {
				document.getElementById('colhead').innerHTML = '<th class="dm_linie">Linie</th>' +
															   '<th class="dm_ziel">Richtung</th>' + 
															   '<th class="dm_departure">Abfahrt</th>';
				document.getElementById('dm_name').innerHTML = dm_name;
				document.getElementById('abfahrtsmonitorTableBody').innerHTML = anzeige;
				document.getElementById('anzeigen').innerHTML = 'aktualisieren (' + new Date().toLocaleTimeString() + ' Uhr)</a>';
			}
				
	});
	});
}

// Störungsmeldung
function teaser() {
	getXML("https://alt.swu.de/?id=5429&type=61312", function(data) {	
		var xml = data.responseXML;
		if (xml.documentElement.getElementsByTagName("teaseritem")) {
			var items = xml.documentElement.getElementsByTagName("teaseritem");
		}
		else {
			var items = '';
		}
		var teasers = [];
		var anzeige = '';
		if (items.length == '0') {
			document.getElementById('stoerung_body').innerHTML = 'zur Zeit liegen keine Meldungen vor';
			var stoerung_link = document.getElementById('stoerung_link');
			if (document.getElementById('stoerung_link')) {
			document.getElementById('header_buttons').removeChild(stoerung_link);
			}
		}
		else {
			for (var i = 0; i < items.length; i++) {
			teasers[i] = items[i];
			var meldung = teasers[i].getElementsByTagName("teaser")[0].textContent;
			anzeige = anzeige.concat(meldung);	
			}
			document.getElementById('stoerung_body').innerHTML = anzeige;
			
			var stoerung_link = document.createElement("a");
			stoerung_link.href = "#stoerungsinfo";
			stoerung_link.title = "Stoerungsinfo";
			stoerung_link.id = "stoerung_link";
			/* ----- einzeln, IE kanns nicht anders ----- */
			stoerung_link.classList.add("ui-btn-left");
			stoerung_link.classList.add("ui-alt-icon");
			stoerung_link.classList.add("ui-btn");
			stoerung_link.classList.add("ui-btn-icon-notext");
			stoerung_link.classList.add("ui-nodisc-icon");
			stoerung_link.classList.add("ui-corner-all");
			stoerung_link.classList.add("ui-icon-alert");
			stoerung_link.classList.add("ui-btn-b");
			stoerung_link.classList.add("btn-stoerung");
			stoerung_link.setAttribute('data-transition', 'pop');
			stoerung_link.setAttribute('data-rel', 'popup');
			stoerung_link.setAttribute('data-position-to', 'window');
			stoerung_link.innerHtml = "";
	
			if (!document.getElementById('stoerung_link')){
			document.getElementById('header_buttons').appendChild(stoerung_link);
			}
		}
	}); //end getXML
} // end teaser


// Timer für Aktualisierung des Abfahrtsmonitors
function setTimer(newTimer) {
	if (timing) {
		clearInterval(timing);
	}
	document.getElementById('showTimer').innerHTML = newTimer + ' S';
	timer = newTimer*1000;
	timing = window.setInterval(function(timer) {
	if (document.getElementById('Haltestelle')) {
		var dm_nummer = document.getElementById('Haltestelle').value;
	}
	else {
		var url = document.URL;
		var dm_nummer = parseInt(url.substr(-4, 4));
	}
	if (dm_nummer !== '') {
		getStopDM(dm_nummer);
	}
	}, timer);
}

function stopTimer() {
	if (timing) {
		clearInterval(timing);
		document.getElementById('showTimer').innerHTML = '...';
	}
}

// Störungsmeldung
function teaser() {
	getXML("//alt.swu.de/?id=5429&type=61312", function(data) {	
		var xml = data.responseXML;
		if (xml.documentElement.getElementsByTagName("teaseritem")) {
			var items = xml.documentElement.getElementsByTagName("teaseritem");
		}
		else {
			var items = '';
		}
		var teasers = [];
		var anzeige = '';
		if (items.length == '0') {
			document.getElementById('stoerungsBody').innerHTML = 'zur Zeit liegen keine Meldungen vor';
			document.getElementById('stoerungsinfo').innerHTML = '<img src="/theme/infoSW.png" class="stoerungs_logo" alt="Logo Störungsinformation">';
			}
		else {
			for (var i = 0; i < items.length; i++) {
			teasers[i] = items[i];
			var meldung = teasers[i].getElementsByTagName("teaser")[0].textContent;
			anzeige = anzeige.concat(meldung);	
			}
			document.getElementById('stoerungsBody').innerHTML = anzeige;
			document.getElementById('stoerungsinfo').innerHTML = '<img src="/theme/info.png" class="stoerungs_logo" alt="Logo Störungsinformation">';
			}
		}); //end getXML
} // end teaser


$(document).on('click', '#datenschutzlink', function(){
	$('#impressumModal').modal('hide');
});

$('#navbar').on("click", "a", null, function () {
	$('#navbar').collapse('hide');
});

$(document).on('click', '#handyticket', function() {
	$.post('/php/phpsqlajax_post_receiver.php',{rcv: "fct", type: "Handyticket"});
})