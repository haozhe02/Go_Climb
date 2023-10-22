let interval;

function checkNotifications(){
	$.ajax({
		url: '/checkNotifications/',
		type: 'GET',
		success: function(response) {
			if (response.notify) {
				var noti = "";
				var counter = 0;
				for(var i in response.notifications){
					noti  += response.notifications[i] + "\n";
					counter++;
					if (counter >= 5){
						alert(noti);
						noti = "";
						counter = 0;
					}
				};
				if (noti != ""){
					alert(noti);
				};
			}; 
		},
		error: function() {
			console.log("An error occurred");
			clearInterval(interval);
		}
	});
};

function checkAuthentication(){
	$.ajax({
		url: '/checkAuthentication/',
		type: 'GET',
		success: function(response) {
			if (response.is_authenticated) {
				console.log("User is authenticated");
				checkNotifications();

				interval = setInterval(checkNotifications, 5000);
			} else {
				console.log("User is not authenticated");
			}
		},
		error: function() {
			console.log("An error occurred");
			clearInterval(interval);
		}
	});
};

$(document).ready(function() {
    checkAuthentication();
});

(function() {
	'use strict';

	var tinyslider = function() {
		var el = document.querySelectorAll('.testimonial-slider');

		if (el.length > 0) {
			var slider = tns({
				container: '.testimonial-slider',
				items: 1,
				axis: "horizontal",
				controlsContainer: "#testimonial-nav",
				swipeAngle: false,
				speed: 700,
				nav: true,
				controls: true,
				autoplay: true,
				autoplayHoverPause: true,
				autoplayTimeout: 3500,
				autoplayButtonOutput: false
			});
		}
	};
	tinyslider();

	


	var sitePlusMinus = function() {

		var value,
    		quantity = document.getElementsByClassName('quantity-container');

		function createBindings(quantityContainer) {
	      var quantityAmount = quantityContainer.getElementsByClassName('quantity-amount')[0];
	      var increase = quantityContainer.getElementsByClassName('increase')[0];
	      var decrease = quantityContainer.getElementsByClassName('decrease')[0];
	      increase.addEventListener('click', function (e) { increaseValue(e, quantityAmount); });
	      decrease.addEventListener('click', function (e) { decreaseValue(e, quantityAmount); });
	    }

	    function init() {
	        for (var i = 0; i < quantity.length; i++ ) {
						createBindings(quantity[i]);
	        }
	    };

	    function increaseValue(event, quantityAmount) {
	        value = parseInt(quantityAmount.value, 10);

	        console.log(quantityAmount, quantityAmount.value);

	        value = isNaN(value) ? 0 : value;
	        value++;
	        quantityAmount.value = value;
	    }

	    function decreaseValue(event, quantityAmount) {
	        value = parseInt(quantityAmount.value, 10);

	        value = isNaN(value) ? 0 : value;
	        if (value > 0) value--;

	        quantityAmount.value = value;
	    }
	    
	    init();
		
	};
	sitePlusMinus();


})()

