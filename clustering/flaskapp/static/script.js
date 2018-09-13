function markValid(boxId) {
    var box = document.getElementById( boxId );
    var clusterId = boxId.substring(0, boxId.indexOf('VerifyBox'));
    var titleId = clusterId + 'Title';
    var summaryTitle = titleId + 'Summary';
    if ( box.checked ) {
    	var data = getVerifiedClusterData(clusterId);
        document.getElementById(titleId).style.color = "#228B22";
        $('#verifiedNavForm').append("<input type='hidden' id=\"" + clusterId + "data\" name=\"" + clusterId + "\" value=\"" + data + "\">")
        // bounce('#navCheckIcon');
        // $('#navCheckIcon').shake();

        $('#' + clusterId).fadeOut(750, function(){
	        $("#navCheckIcon").effect( "shake", {distance:15, times:3}, 800 );
	        var badDocs = document.getElementById(clusterId).getElementsByClassName('badDoc');
	        if(badDocs.length > 0){
	        	$("#navXIcon").effect( "shake", {distance:15, times:3}, 800 );
	        }
	        var cluster = document.getElementById(clusterId);
	        $('#verifiedContainer').append(cluster);
	        var numDocs = cluster.getElementsByClassName('docBody')[0].getElementsByTagName('div').length;
	        // cluster.getElementsByClassName('docCount')[0].textContent
	        cluster.getElementsByClassName('docCount')[0].textContent = "Documents in cluster: " + numDocs;

	        // $('#' + clusterId).show();

	        var summary = document.getElementById(clusterId + "Summary").cloneNode(true);
	        console.log(summary);
	        summary.id = clusterId + "VerSummary";
	        var docCountText = summary.getElementsByClassName('summaryDocCount')[0].textContent;
	        console.log(docCountText);
	        var totClusterDocs = docCountText.substring(0, docCountText.indexOf(" "));
	        var numInvInCluster = docCountText.substring(docCountText.lastIndexOf(" ") + 1, docCountText.lastIndexOf(")"));

	        var netNumDocs = parseInt(totClusterDocs) - parseInt(numInvInCluster);
	        if(parseInt(netNumDocs) === 1){
	        	summary.getElementsByClassName('summaryDocCount')[0].textContent = netNumDocs + " doc";
	        }
	        else{
	        	summary.getElementsByClassName('summaryDocCount')[0].textContent = netNumDocs + " docs";	
	        }
	        
	        $('#verifiedSummaries').append(summary);

	        document.getElementById('homeNumDocsRemaining').textContent = document.getElementById('homeContainer').getElementsByClassName('sentenceTxt').length;        	
        });        

        document.getElementById(summaryTitle).style.color = "#228B22";


        // document.getElementById(clusterId).getElementsByClassName("docBody")[0].style.display = "none";
        // var topWords = document.getElementById(clusterId).getElementsByClassName("topWord");
        // for(var i = 0; i < topWords.length; i++){
        // 	topWords[i].style.display = "none";
        // }
        // document.getElementById(clusterId).getElementsByClassName("wordHeader")[0].style.display = "none";


    }
    else{
    	box.nextSibling.textContent = "\t Verify";
    	document.getElementById(titleId).style.color = "#000000";
        document.getElementById(summaryTitle).style.color = "#007BFF";

    	$('#' + clusterId + 'data').remove();
    	// var badDocs = document.getElementById(clusterId).getElementsByClassName('badDoc');
     //    for(var i = 0; i < badDocs.length; i++){
     //    	badDocs[i].style.display = "block";
     //    }
    	document.getElementById(clusterId).getElementsByClassName("docBody")[0].style.display = "block";
        var topWords = document.getElementById(clusterId).getElementsByClassName("topWord");
        for(var i = 0; i < topWords.length; i++){
        	topWords[i].style.display = "block";
        }
        document.getElementById(clusterId).getElementsByClassName("wordHeader")[0].style.display = "block";

    }

}

function checkDocument(checkId){
	var sentenceId = checkId.substring(0, checkId.indexOf('check'));
	var element = document.getElementById(sentenceId);
	if(element.className === "badDoc"){
		var clusterId = sentenceId.substring(0, sentenceId.indexOf("sentence"));
		var numInvalid = parseInt($('#' + clusterId + 'summaryDocCount > i').text());
		$('#' + clusterId + 'summaryDocCount > i').text(numInvalid - 1);
		element.className = "goodDoc";
	}
	else{
		element.classList.toggle("goodDoc");
		element.classList.toggle("neutralDoc");
	}
	
}

function invalidateDocument(xId){
	var sentenceId = xId.substring(0, xId.indexOf('X'));
	var element = document.getElementById(sentenceId);
	var clusterId = sentenceId.substring(0, sentenceId.indexOf("sentence"));
	var numInvalid = parseInt($('#' + clusterId + 'Summary .summaryDocCount > i').text());
	if(element.className === "badDoc"){
		element.className = "neutralDoc";
		$('#' + clusterId + 'Summary .summaryDocCount > i').text(" " + parseInt(numInvalid - 1));
		$('#' + clusterId + sentenceId + 'badData').remove();
	}
	else{
		element.className = "badDoc";
		$('#' + clusterId + 'Summary .summaryDocCount > i').text(" " + parseInt(numInvalid + 1));

		var span = element.getElementsByClassName('sentenceTxt')[0];
	    var str = span.innerHTML.substring(4, span.innerHTML.lastIndexOf('" (')) + span.innerHTML.substring(span.innerHTML.lastIndexOf('(')) + '\n';
	    str = str.replace(/"/g, "'").trim();
	    $('#invalidNavForm').append("<input type='hidden' name=\"" + clusterId + sentenceId + "badData\" value=\"" + str + "\">");

	    if($('#miscCluster').is(":hidden")){
	    	$('#miscCluster').show();
	    	$("#homeSummaries").append("<div class='summary'>\
	    									<a href='#miscCluster' id='miscTitleSummary'> Miscellaneous </a>\
	    									<div id='miscSummaryXDiv'><i class='fas fa-times fa-2x'></i></div>\
	    									<div id='miscsummaryDocCount'></div>\
	    								</div>");

	    	var summaries = document.getElementsByClassName('summary');
	    	for(var i = 0; i<summaries.lenght; i++){
	    		console.log(summaries[i]);
	    	}
	    	var numSummaries = summaries.length;
	    	if(numSummaries > 0){
	    		$('#miscSummaryXDiv').height($('.summaryFirstWord').height());
	    	}
	    	console.log("num summaries: " + numSummaries);
	    	var screenPercent = 100/numSummaries + "%";
			$('#homeSummaries .summary').css('width', screenPercent);
	    }

	    $('#' + sentenceId).fadeOut(650, function(){
            $('#' + sentenceId).appendTo('#miscBody').fadeIn(500, function(){
            	var numMisc = document.getElementById('miscCluster').getElementsByClassName('sentenceTxt').length;
            	if(numMisc === 1){
            		$('#miscsummaryDocCount').text(numMisc + " doc");
            	}
            	else{
            		$('#miscsummaryDocCount').text(numMisc + " docs");
            	}
            });
        });

        

	}
	
}


// function trackRemovedStopWord(swId){
// 	$('#form').append("<input type='hidden' name='removedStopWord' value='" + document.getElementById(swId).textContent.trim() + "'>");
// 	$('#' + swId).remove();
// }

function getVerifiedClusterData(clusterId){
	var str = "";
	var cluster = document.getElementById(clusterId);
	var rightSide = cluster.getElementsByClassName('col-md-3')[0];
	var clusterTitle = document.getElementById(clusterId + "Title").innerHTML.trim();
	var topWords = rightSide.getElementsByClassName('topWord');
	var docs = cluster.getElementsByClassName('docBody')[0];
	var goodDocs = docs.querySelectorAll('.goodDoc,.neutralDoc');
	// var goodDocs = docs.getElementsByClassName('goodDoc');

	str += clusterTitle + "\n";
	for(var i = 0; i < topWords.length; i++){
		str += topWords[i].innerHTML.trim() + "\n";
	}

	for(var i=0; i<goodDocs.length; i++)
    {
    	var span = goodDocs[i].getElementsByClassName('sentenceTxt')[0];
        // str += goodDocs[i].textContent.trim().substring(4, goodDocs[i].textContent.lastIndexOf('\"')) + goodDocs[i].textContent.trim().substring(goodDocs[i].textContent.lastIndexOf('\"') + 1) + "\n";

        str += span.innerHTML.substring(4, span.innerHTML.lastIndexOf('" (')) + span.innerHTML.substring(span.innerHTML.lastIndexOf('(')) + '\n';
    }
    return str.replace(/"/g, "'").trim();
}

function showHowTo(){
	alert("Click on individual sentences in each cluster to mark them as irrelevant. After pruning, mark cluster as valid with the 'Verify' checkbox. \n\nClick 'See Verified Clusters' button to go to page of valid clusters. \n\n'Recalculate Invalid Documents' to run k-means algorithm on the leftover off-topic sentences");
}