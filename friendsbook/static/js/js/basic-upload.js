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
      if (data.result.is_valid) 
        document.getElementById("cover_background_image").src=data.result.url;
      else console.log('having some problem')
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


  $("#groupCoverPhoto").fileupload({
    dataType: 'json',
    done: function (e, data) {
      if (data.result.is_valid) {
		  var str='url("'+data.result.url+'")'
        document.getElementById("cover_background").style.backgroundImage=str;
		}
      }
  });


  $('#groupcover').click(function() {
	  console.log('done')
	  $('#groupCoverPhoto').click();

  });
});
