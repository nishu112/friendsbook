$(function () {

	$("div.upper_post").on("click", ".like", function () {
		console.log("working");
		var type=$(this).attr("type");
    var li = $(this).closest("li");
    var id = $(li).attr("post-id");
		var upper_post=$(this).closest(".upper_post")
    var csrf = $(li).attr("csrf");
		console.log(id)
		console.log(type)
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
				console.log($(".like .text", li));
        if ($(".like", upper_post).hasClass("unlike")) {
          $(".like", upper_post).removeClass("unlike");
          $(".like .text", upper_post).text("Like");
        }
        else {
          $(".like", upper_post).addClass("unlike");
          $(".like .text", upper_post).text("Unlike");
        }
        $(".like .like-count", upper_post).text(data);
				console.log(data)
      }
    });
    return false;
  });

$("div.upper_post").on("click", ".delete_status", function () {
 console.log('delete post')
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
			console.log("Delete status")
			$(li).fadeOut(400, function () {
          $(li).remove();
        });
		}
	});

});


	$("div.Allcomments").on("click", ".like", function () {
		console.log("comment likes")
    id=$(this).closest('.particularcomment').attr('id')
		type=$(this).attr('type')
		particularcomment=$(this).closest('.particularcomment')
		 var li = $(this).closest("li");
		var csrf = $(li).attr("csrf");
		console.log(id);
		console.log(type);
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


$("div.Allcomments").on("click", ".delete_comment", function () {
	console.log("delete comment ")
	id=$(this).closest('.particularcomment').attr('id')
	type=$(this).attr('class')
	particularcomment=$(this).closest('.particularcomment')
	var li = $(this).closest("li");
	var csrf = $(li).attr("csrf");
	console.log(id);
	console.log(type);

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
			console.log("Deleted the comments")
			$(particularcomment).fadeOut(400, function () {
          $(particularcomment).remove();
        });
		}

});
});


$("div.post_button").on("click", ".comment", function () {
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


$(".comments").on("keydown", "input[name='post']", function (evt){
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
					 console.log("yep")
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