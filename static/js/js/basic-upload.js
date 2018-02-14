$(function () {

  $("#mycover").click(function () {
    $("#fileupload1").click();
  });

  $("#mypic").click(function () {
    $("#fileupload2").click();
  });
  
  $("#fileupload1").fileupload({
    dataType: 'json',
    done: function (e, data) {
      if (data.result.is_valid) {
		  var str='url("'+data.result.url+'")'
		  console.log("NOpe")
		  console.log(str)
        document.getElementById("cover_background").style.backgroundImage=str;
      }
        /*$("#gallery tbody").prepend(
          "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
        )*/
      }
  });


  $("#fileupload2").fileupload({
    dataType: 'json',
    done: function (e, data) {
      if (data.result.is_valid) {
        var str='"'+data.result.url+'"'
		console.log(str)
        document.getElementById("my_profile_pic").src=data.result.url;
      }
    }
  });
});
