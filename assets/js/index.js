/*global
	$
*/
$(document).ready(function () {

	'use strict';

	var $grid = $('.grid');

	if ($grid.length > 0) {
		$grid.imagesLoaded().progress(function (instance, image) {
			var $gridItem = $(image.img).parents('.grid-item');
			$gridItem.removeClass('loading');
			if (image.isLoaded) {
				$gridItem.addClass('loaded');
			} else {
				$gridItem.addClass('unloaded');
			}
			$gridItem.fadeIn('fast');
		}).always(function () {
			$('.spinner').fadeOut('fast');
			$('.grid').masonry({
				itemSelector: '.grid-item'
			});
			$('.pagination, .widgets, footer').show();
		});
	} else {
		$('.widgets, footer').show();
	}
});
