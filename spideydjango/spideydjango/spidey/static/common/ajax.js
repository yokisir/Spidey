/*
	This js is used for AJAX for SPIDEY 1.0
	writer:smallyoki
	Test Environment:Chrome 50.0
	Warning:This is test in Chrome,not use in IE5/IE6!
	Last Modified by Yoki at 2016.6.29
*/

var flag=true;			//flag is true means the states is Scan,false means the states is OK

function ScanItNow(model)
{
	if (flag==false && model=="database") {
		document.getElementById("inforart").className="hiddenart";
		document.getElementById("mainart").className="viewmainart";

		//recover the view
		document.getElementById("inputurl").style.display="inline";
		document.getElementById("submiturl").value="Scan This URL";
		document.getElementById("submiturl").style.marginTop="32px";
		document.getElementById("submiturl").style.background="#ff766d";
		document.getElementById("submiturl").style.cursor="pointer";

		document.getElementById("inputurl").focus();

		flag=true;
		return;
	};
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
	document.getElementById("submiturl").disabled="disabled";
	document.getElementById("submiturl").style.background="#dd4c44";
	document.getElementById("submiturl").style.cursor="wait";

	xmlhttp.onreadystatechange=function()
	{
		if (xmlhttp.readyState==4 && xmlhttp.status==200) {
			var phish = "";
			var lastscantime = "";
			var state="unsafe"

			//Get the return text
			var urlobject = eval("("+xmlhttp.responseText+")");
			if (model=="database") {
				state=urlobject.state;
				totalscore=0;
				lastscantime=urlobject.lastscantime
			};
			if (state=="safe") {
				inforstring="<table class='infortable' id='infortable'><tr><td>URL:</td><td><a>";
				var patt = new RegExp('http');
				var ret_test = patt.test(surl);
				aurl=surl;
				if (!ret_test) {
					aurl="http://"+surl;
				}
				if(surl.length>30)inforstring+="<a href="+aurl+" target='_blank'>"+surl.substr(0,40)+"...</a>";
				else inforstring+="<a href="+aurl+" target='_blank'>"+surl+"</a>";					
				inforstring+="<tr><td>TotalScore:</td><td id='totalscore'>"+totalscore+" (data from 360)</td></tr>"
				inforstring+="<tr><td>LastScanTime:</td><td>"+lastscantime+"</td></tr></table>";
			}
			else{
				phish=urlobject.phish;
				download=urlobject.download;
				totalscore=urlobject.dangerlevel;
				isfake=urlobject.isfake;
				isdistort=urlobject.isdistort;
				istrojan=urlobject.istrojan;
				sdscore=urlobject.staticdetection;
				lastscantime=urlobject.lastscantime;

				//deal with the new innerHTML
				inforstring="<table class='infortable' id='infortable'><tr><td>URL:</td><td><a>";
				var patt = new RegExp('http');
				var ret_test = patt.test(surl);
				aurl=surl;
				if (!ret_test) {
					aurl="http://"+surl;
				}
				if(surl.length>30)inforstring+="<a href="+aurl+" target='_blank'>"+surl.substr(0,40)+"...</a>";
				else inforstring+="<a href="+aurl+" target='_blank'>"+surl+"</a>";
				inforstring+="<tr><td>Static Detection:</td><td id='sdscore'>"+sdscore+"</td></tr>"
				inforstring+="</a></td></tr><tr><td>Phish / Download link:</td><td id='phishdownload'>"+phish+" / "+download+" (data from Jinshan)</td></tr>"
				inforstring+="<tr><td>Fake / Distort / Trojan:</td><td id='fakedistortrtojan'>"+isfake+" / "+isdistort+" / "+istrojan+" (data from 360)</td></tr>"
				inforstring+="<tr><td>TotalScore:</td><td id='totalscore'>"+totalscore+" (data from 360)</td></tr>"
				inforstring+="<tr><td>LastScanTime:</td><td>"+lastscantime+"</td></tr></table>";
			}
			//document.getElementById("mainart").style.display="none";
			document.getElementById("mainart").className="hiddenart";
			document.getElementById("inforart").className="viewinforart";
			//document.getElementById("inforart").style.display="block";
			document.getElementById("inforart").innerHTML=inforstring;

			//change the color of font of phish
			dangercolor=['grey','green','orange','red'];
			sdscoredangertitle=['Safe web','Risky web!','Dangerous web!'];
			phidangertitle=['Unknow web','Safe web','Risky web!','Phish web!'];
			downdangertitle=['Unknow links','Safe links','Dangerous links!'];
			fakedangertitle=['Not Fake','Fake web!'];
			distortdangertitle=['Not distort','Distort web!'];
			trojandangertitle=['Not trojan','Trojan web!'];
			totaldangertitle=['Safe web','Dangerous web!'];
			if (state=="unsafe") {
				document.getElementById("sdscore").style.color=dangercolor[sdscore+1];
				document.getElementById("sdscore").title=sdscoredangertitle[sdscore];
				document.getElementById("phishdownload").style.color=dangercolor[Math.max(phish,download)+1];
				phidowntitle=phidangertitle[phish+1]+" / "+downdangertitle[download+1]
				document.getElementById("phishdownload").title=phidowntitle;
				document.getElementById("fakedistortrtojan").style.color=dangercolor[Math.max(isfake,isdistort,istrojan)+1];
				fakedistortrtojantitle=fakedangertitle[Math.floor(isfake/2)]+" / "+distortdangertitle[Math.floor(isdistort/2)]+" / "+trojandangertitle[Math.floor(istrojan/2)]
				document.getElementById("fakedistortrtojan").title=fakedistortrtojantitle;
			}
			document.getElementById("totalscore").style.color=dangercolor[totalscore+1];
			document.getElementById("totalscore").title=totaldangertitle[Math.floor(totalscore/2)];
			document.getElementById("inputurl").style.display="none";
			document.getElementById("submiturl").value="OK";
			if (state=="safe") {
				document.getElementById("submiturl").style.marginTop="34px";
			}
			else{
				document.getElementById("submiturl").style.marginTop="28px";
			}
			document.getElementById("submiturl").disabled="";
			document.getElementById("submiturl").style.background="#ff766d";
			document.getElementById("submiturl").style.cursor="pointer";
			document.getElementById("submiturl").focus();
			//document.getElementById("submiturl").onclick=function(){history.go(0)};
		};
	}

	if (model=="now") {
		xmlhttp.open("POST","scanurlnow",true);
	}
	else{
		xmlhttp.open("POST","scanurlfromdatabase",true);
	}
	xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	xmlhttp.send("url="+surl);

	flag=false;
}