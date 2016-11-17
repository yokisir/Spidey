/*
	This is js used for SPIDEY 1.0
	writer:smallyoki
	Test Environment:Chrome 50.0
	Last Modified by Yoki at 2016.6.27
*/

window.onload=changeondrag;

//Prohibit picture to be draged
function imgdragstart(){return false;}
function changeondrag(){
	for(i in document.images)document.images[i].ondragstart=imgdragstart;
}

//Change Section to DerivedData
function DerivedData(){
	//view different a in head
	document.getElementById("Backa").style.display="inline";
	document.getElementById("DerivedDataa").style.display="none";

	//view different section in body
	document.getElementById("DerivedDataSec").style.display="block";
	document.getElementById("PageContentSec").style.display="none";
	document.getElementById("keywordofurls").focus();

}

//Change Section for back DerivedData_back
function DerivedData_back(){
	//view different a in head
	document.getElementById("Backa").style.display="none";
	document.getElementById("DerivedDataa").style.display="inline";

	//view different section in body
	document.getElementById("DerivedDataSec").style.display="none";
	document.getElementById("PageContentSec").style.display="block";
	document.getElementById("inputurl").focus();

}