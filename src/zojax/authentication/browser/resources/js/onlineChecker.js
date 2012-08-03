function makeOnline(){ 
	var url = $("head").attr('portal');
	var params = {};
	$.jsonRPC.setup({
		  endPoint: url + '/++skin++JSONRPC.authentication'
		});
	$.jsonRPC.request('incOnline', {params: params});
	window.setTimeout("makeOnline(url);", 270000 + getRandomInt(0, 2000));
}

function getRandomInt(min, max)
{
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getOnlineNumber(element_id)
{
	var url = $("head").attr('portal');
	var params = {};
	$.jsonRPC.setup({
		  endPoint: url + '/++skin++JSONRPC.authentication'
		});
	$.jsonRPC.request('onlineNumber', {
		  params: params,
		  success: function(result) {
			  document.getElementById(element_id).innerHTML = result.result;
		  }
		});
}


