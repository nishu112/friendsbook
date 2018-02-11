function showfriendlist(){
	$.ajax({
        url: '/ajax/users/profile/friend_list/',
	type:'get',
        dataType: 'json',
        success: function (data) {
			console.log(data);
			document.getElementById('profileonclickbuttons').innerHTML=data;
	
        }
      });
    }