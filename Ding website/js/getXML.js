// JavaScript Document

function getXML(url, callback) {
      var request = window.ActiveXObject ?
          new ActiveXObject('Microsoft.XMLHTTP') :
          new XMLHttpRequest;

      request.onreadystatechange = function() {
        if (request.readyState == 4) {
          callback(request, request.status);
        }
      };

      request.open('GET', url, true);
      request.send(null);
}

