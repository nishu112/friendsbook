$(function () {


		$(document).on("click", "div.upper_post .like", function () {

		var type=$(this).attr("type");
		var li = $(this).closest("li");
		var id = $(li).attr("post-id");
		var upper_post=$(this).closest(".upper_post");
		var csrf = $(li).attr("csrf");

    $.ajax({
      url: '/ajax/like_post/',
      data: {
				'id':id,
				'type':type,
        'csrfmiddlewaretoken': csrf,
      },
      type: 'POST',
      cache: false,
      success: function (data) {

        if ($(".like", upper_post).hasClass("unlike")) {
          $(".like", upper_post).removeClass("unlike");
          $(".like .text", upper_post).text("Like");
        }
        else {
          $(".like", upper_post).addClass("unlike");
          $(".like .text", upper_post).text("Unlike");
        }
        $(".like .like-count", upper_post).text(data);

      }
    });
    return false;
  });

$(document).on("click", "div.upper_post .delete_status", function () {

	var li = $(this).closest("li");
	var id = $(li).attr("post-id");
	var upper_post=$(this).closest(".upper_post")
	var csrf = $(li).attr("csrf");
	type=$(this).attr('class')

	$.ajax({
		url: '/ajax/deleteCommentPost/',
		data: {
			'id':id,
			'type':type,
			'csrfmiddlewaretoken': csrf,
		},
		type: 'POST',
		cache: false,
		success: function (data) {

			$(li).fadeOut(400, function () {
          $(li).remove();
        });
		}
	});

});


	$(document).on("click", "div.Allcomments .like", function () {

    id=$(this).closest('.particularcomment').attr('id')
		type=$(this).attr('type')
		particularcomment=$(this).closest('.particularcomment')
		 var li = $(this).closest("li");
		var csrf = $(li).attr("csrf");

		$.ajax({
			url: '/ajax/like_post/',
			data:{
				'id':id,
				'type':type,
				'csrfmiddlewaretoken': csrf,
			},
			type:'POST',
			dataType: 'json',
			success: function (data) {
        if ($(".like", particularcomment).hasClass("unlike")) {
          $(".like", particularcomment).removeClass("unlike");
          $(".like .text", particularcomment).text("Like");
        }
        else {
          $(".like", particularcomment).addClass("unlike");
          $(".like .text", particularcomment).text("Unlike");
        }
        $(".like .like-count", particularcomment).text(data);
			}

	});
});


$(document).on("click", "div.Allcomments .delete_comment", function () {

	id=$(this).closest('.particularcomment').attr('id')
	type=$(this).attr('class')
	particularcomment=$(this).closest('.particularcomment')
	var li = $(this).closest("li");
	var csrf = $(li).attr("csrf");


	$.ajax({
		url: '/ajax/deleteCommentPost/',
		data:{
			'id':id,
			'type':type,
			'csrfmiddlewaretoken': csrf,
		},
		type:'POST',
		dataType: 'json',
		success: function (data) {

			$(particularcomment).fadeOut(400, function () {
          $(particularcomment).remove();
        });
		}

});
});


$(document).on("click", "div.post_button .comment", function () {

	var li = $(this).closest("li");
	if($(".comments", li).css('display') != 'none')
			{
				$(".comments", li).slideUp();
			}
	else
	{
		$(".comments", li).show();
		$(".comments input[name='post']", li).focus();
		var sid = $(li).attr("post-id");
		$.ajax({
		url: '/ajax/loadcomment/',
		data:{
			'sid':sid,
		},
		type:'GET',
		dataType: 'json',
		beforeSend: function () {
          $(".Allcomments", li).html("<li class='loadcomment'><img src='/static/img/loading.gif'></li>");
        },
		success: function (data) {
			$(".Allcomments", li).html(data);
			return;
			}
		});
		}

});

$(document).on("click", "div.Allcomments .edit_comment", function () {


particularcomment=$(this).closest('.particularcomment')

	orignalcomment=$(this).closest('.orignalcomment')
	editcomment=$(particularcomment).children('.editcomment');

	//editcomment=$(this).closest('.editcomment')
	$(orignalcomment).hide()
	$(editcomment).show()


	});




$(document).on("keydown", ".editcomment input[name='post']", function (evt){
	var keyCode = evt.which?evt.which:evt.keyCode;
  if (keyCode == 13) {
 	 form = $(this).closest("form");
 	 container = $(this).closest(".comments");
	 particularcomment=$(this).closest('.particularcomment')
	 editcomment=$(this).closest('.editcomment')
	 orignalcomment=$(particularcomment).children('.orignalcomment')
	 currenttext=$(editcomment).children('input[name="post"]')
	 oldtext=$(orignalcomment).children('')

 	 $.ajax({
 		 url: "/ajax/editcomment/",
 		 data: $(form).serialize(),
 		 type: 'POST',
 		 cache: false,
 		 success: function (data) {
 			 if(data==0)
				 {alert('Something Fishy Going on')
				 return;}

				 $(particularcomment).html(data)
 		 }
 	 });
 	 return false;
  }
 });

$(document).on("keydown", ".comments .newcomment input[name='post']", function (evt){
	 var keyCode = evt.which?evt.which:evt.keyCode;
	 if (keyCode == 13) {
		 var form = $(this).closest("form");
		 var container = $(this).closest(".comments");
		 var input = $(this);
		 $.ajax({
			 url: '/ajax/loadcomment/',
			 data: $(form).serialize(),
			 type: 'POST',
			 cache: false,
			 beforeSend: function () {
				 $(input).val("");
			 },
			 success: function (data) {
				 $(".Allcomments", container).append(data);
				 if ($(".Allcomments li", container).hasClass("empty")) {

          deletedelement= $(".Allcomments li", container);
					 $(deletedelement).fadeOut(400, function () {
		           $(deletedelement).remove();
		         });
					 }
			 }
		 });
		 return false;
	 }
 });

});
