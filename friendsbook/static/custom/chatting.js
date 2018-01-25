
function addfriend(fuser) {
	$.ajax({
        url: '/ajax/AddFriend/',
        data:{
		  'fuser':fuser
        },
        dataType: 'json',
        success: function (data) {
			if(data==0)
				document.getElementById(fuser).innerHTML="Add Friend";
			else
				document.getElementById(fuser).innerHTML="UnFriend";
        }
      });
    }


	
	
//chatting
	
	