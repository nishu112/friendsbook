$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
	});
	var chat_with="";
	var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
	var socket = new WebSocket(ws_scheme+'://' + window.location.host + '/users/');
	var socket = new WebSocket(ws_scheme+'://' + window.location.host + '/{{user.username}}/');

    socket.onopen = function open() {

      console.log('WebSockets connection created.');
    };

    socket.onmessage = function message(event) {
      var data = JSON.parse(event.data);
	  var type = data['type'];
	  var user = data['user'];
	  //did this logic to satisfy condition
	  //so that message will recieve only if
	  //we clicked on the link
	  if(type=='online'){
	  var online_user=$('#sidebar ul li a div div').filter(function(){
	  return $(this).data('username')==user;
	  });
	  var fname=data['fname'];
	  var lname=data['lname'];
	  if(lname){}
	  else lname="";
	  if(data['is_logged_in'])
	  online_user.html('<span style="background: rgb(66, 183, 42); border-radius: 50%; display: inline-block;float:right; height: 6px; margin-left: 4px;float:right;margin-top: 17px; width: 6px;"></span>');
	  else
	  online_user.html('');
	  return;
	  }
	  var text = data['text'];
	  var fuser = data['fuser'];

	  if(chat_with!=fuser)	return;
	  if('{{user.username}}'==user)
      $('#msg-list').append('<span data-placement="right" data-toggle="tooltip" title="'+data['time']+'"> <p class=" text-right list-group-item">' +data['text'] + '</p></span>')

	  else
	  $('#msg-list').append('<span data-placement="right" data-toggle="tooltip" title="'+data['time']+'"> <p class="text-left list-group-item">' +data['text'] + '</p></span>')

	  $('#msg-list').scrollTop(document.getElementById("msg-list").scrollHeight);
	  $(document).ready(function(){
		$('[data-toggle="tooltip"]').tooltip();
		});
    };
    if (socket.readyState == WebSocket.OPEN) {
      socket.onopen();
    }

    $("#chatform").on("submit", function(event) {
		if(chat_with=="")
			{alert("please select the user");return;}
		var text=document.getElementById("text_message").value;
		var fuser=chat_with;
		var user='{{user.username}}';

		var message ={
			text,fuser,user
		};
        socket.send(JSON.stringify(message));
        document.getElementById("text_message").value="";
        return false;
    });

	function comment(obj){
	sid=obj.parentNode.parentNode.parentNode.parentNode.id;
	commentid='comment-'+sid;
	text=document.getElementById(commentid).value;
	if(text=="")	return;
	$.ajax({
	url: '/ajax/comment/',
	data:{
	  'text':text,
	  'sid':sid
	},
	dataType: 'json',
	success: function (data) {
		if( data!=0){
			$('#Allcomments'+sid).append("<p> {{user.username}} :"+data +"</p>");
			document.getElementById(commentid).value="";
			}
		else
			alert("not send");
		}
	});
	}

	function like(obj) {
	var type=obj.id;
	console.log(type);
	//4 times for comment likes
	//3 times for post like
	if(obj.id=='comment_like')
		{id=obj.parentNode.parentNode.parentNode.parentNode.id;
		likeid='comment-'+id;
		}
	else
		{id=obj.parentNode.parentNode.parentNode.id;
		likeid='like-'+id;
		}
	console.log(id);
	$.ajax({
		url: '/ajax/like_post/',
		data:{
		  'id':id,
		  'type':type
		},
		dataType: 'json',
		success: function (data) {
			if( data!=0)
				document.getElementById(likeid).innerHTML=data;
			else
				document.getElementById(likeid).innerHTML="";
		}
	  });
	}

	function change_post_comment(obj){
		type=obj.parentNode.parentNode.parentNode.id;
		alert("are u sure?");
		var id;
		if(type=="status")
			id=obj.parentNode.parentNode.parentNode.parentNode.parentNode.id;
		else if(type=="comment")
			id=obj.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.id;
		else
			{console.log('error while getting the id');
			return;
			}
		console.log(type);
		console.log(id);
		$.ajax({
			url:'/ajax/deleteCommentPost/',
			data:{
			'id':id,
			'type':type
			},
			dataType:'json',
			success:function(data){
				if(type=="status")
				document.getElementById(id).style.display="none";
				if(type=="comment")
				document.getElementById(id)="";
				}
			});
	}
	function showcomment(obj){
		id=obj.parentNode.parentNode.parentNode.id;
		id='comment_class'+id;
		var isDisplayBlock=document.getElementById(id).style.display;
		if(isDisplayBlock=="none")
		document.getElementById(id).style.display="block";
		else
		document.getElementById(id).style.display="none";

		}
	function showLiveResult(str){
	console.log('hii');
		if(str.length==""){
			document.getElementById("liveSearchResult").innerHTML="";
			document.getElementById("liveSearchResult").style.border="0px";
			return;
			}
		$.ajax({
		url: "/ajax/liveSearch/",
		data:{
		  'search':str,
		},
		dataType: 'json',
		success: function (data) {
		console.log(data)
			var data=JSON.parse(data);
			var content="<table>";
			$.each (data, function (val) {
				console.log(data[val].fields.username);
				if(data[val].fields.lname==null)
				content+='<tr><td>'+'<a  href='+'/users/profile/'+data[val].fields.slug+'>'+data[val].fields.fname+'</td></tr>';
				else
				content+='<tr><td>'+'<a  href='+'/users/profile/'+data[val].fields.slug+'>'+data[val].fields.fname+' '+data[val].fields.lname+'</td></tr>';
			});
			content+='</table>'
			document.getElementById("liveSearchResult").innerHTML=content;
		}
		});
		}
