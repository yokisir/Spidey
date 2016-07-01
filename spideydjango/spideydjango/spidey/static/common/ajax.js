/*
	This js is used for AJAX for SPIDEY 1.0
	writer:smallyoki
	Test Environment:Chrome 50.0
	Warning:This is test in Chrome,not used in IE5/IE6!
	Last Modified by Yoki at 2016.6.29
*/

var flag=true;			//flag is true means the states is Scan,false means the states is OK

function loadXMLDoc()
{
	if (flag){
		var xmlhttp;
		var surl;			//Used to record the submitted url
		var inforstring;	//Used to restore the loadXML
		xmlhttp=new XMLHttpRequest();
		surl=document.getElementById("inputurl").value+'';

		//if the input box is null, return false
		if (surl==''){
			alert("The url can not be null!");
			document.getElementById("inputurl").focus();
			return false;
		}

		//Change The view of DOM when waiting for respond
		document.getElementById("submiturl").value="loading...";
		document.getElementById("submiturl").style.background="#dd4c44";
		document.getElementById("submiturl").style.cursor="wait";
		//alert();

		xmlhttp.onreadystatechange=function()
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) {
				var dangerlevel = "";
				var lastscantime = "";

				//Get the return text
				var urlobject = eval("("+xmlhttp.responseText+")");
				dangerlevel=urlobject.dangerlevel;
				lastscantime=urlobject.lastscantime;

				//deal with the new innerHTML
				inforstring="<table class='infortable' id='infortable'><tr><td>URL:</td><td>";
				if(surl.length>30)inforstring+=surl.substr(0,40)+"...";
				else inforstring+=surl.substr(0,40);
				inforstring+="</td></tr><tr><td>DangerLevel:</td><td id='dangerlevel'>"+dangerlevel+"</td></tr>"
				inforstring+="<tr><td>LastScanTime:</td><td>"+lastscantime+"</td></tr></table>";

				//document.getElementById("mainart").style.display="none";
				document.getElementById("mainart").className="hiddenart";
				document.getElementById("inforart").className="viewinforart";
				//document.getElementById("inforart").style.display="block";
				document.getElementById("inforart").innerHTML=inforstring;

				//change the color of font of dangerlevel
				if (dangerlevel == '4' || dangerlevel == '5') {
					dangercolor ='red';
				}
				else if (dangerlevel == '3') {
					dangercolor = 'orange';
				}
				else
					dangercolor = 'blue';
				document.getElementById("dangerlevel").style.color=dangercolor;

				document.getElementById("inputurl").style.display="none";
				document.getElementById("submiturl").value="OK";
				document.getElementById("submiturl").style.background="#ff766d";
				document.getElementById("submiturl").style.cursor="pointer";
				document.getElementById("submiturl").focus();
				//document.getElementById("submiturl").onclick=function(){history.go(0)};
			};
		}


		xmlhttp.open("POST","scanurl",true);
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		xmlhttp.send("url="+surl);

		flag=false;
	}
	else{		//return to scan

		document.getElementById("inforart").className="hiddenart";
		//document.getElementById("inforart").style.display="none";
		document.getElementById("mainart").className="viewmainart";
		//document.getElementById("mainart").style.display="block";

		//recover the view
		document.getElementById("inputurl").style.display="inline";
		document.getElementById("submiturl").value="Scan This URL";
		document.getElementById("submiturl").style.background="#ff766d";
		document.getElementById("submiturl").style.cursor="pointer";

		document.getElementById("inputurl").focus();

		flag=true;
	}
}