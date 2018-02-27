$(function () {
	$(document).on("click", ".add_friendbutton button", function () {
	particularuser=$(this).closest('.particularuser')
	console.log(particularuser)
	csrf=$(particularuser).attr('csrf')
	console.log(csrf)
	user=$(particularuser).attr('user')
	performaction=$(this).attr('performaction')
	actiontype=$(this).attr('actiontype')
	prev=this
	$.ajax({
        url: '/ajax/AddFriend/',
        data:{
		  'fuser':user,
		  'type':performaction,
			'csrfmiddlewaretoken':csrf,
        },
				type:'POST',
        success: function (data) {
					if(data==0){
						alert("something fishy")
						return;
					}
					if (performaction=='Send')
						{$(prev).html("Cancel Request")
						 $(prev).attr("performaction","Cancel");}
					else if(performaction=='Cancel')
						{$(prev).html("Send Request")
						$(prev).attr("performaction","Send");}
					else if(performaction=='Confirm')
						{$(prev).html("Unfriend")
						$(prev).attr("performaction","Unfriend")

						$('.type2').remove()
						if($(prev).hasClass('type1')){
							$(prev).removeClass('type1')
							$(prev).addClass('type2')
							$(prev).attr("actiontype","type2")
						}
					}
					else if( performaction=='Delete')
						{
							button=$('.type1')
							$(button).html("Send Request")
							$(button).attr("performaction","Send")
							$(prev).remove()
						}
					else if(performaction='Unfriend'){
						$(prev).html("Send Request")
						$(prev).attr("performaction","Send")
					}
        }
      });

	});
});