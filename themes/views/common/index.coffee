$(document).ready ->
  'use strict'
  $grid = $('.grid')
  if $grid.length > 0
    $grid.imagesLoaded().progress((instance, image) ->
      $gridItem = $(image.img).parents('.grid-item')
      $gridItem.removeClass 'loading'
      if image.isLoaded
        $gridItem.addClass 'loaded'
      else
        $gridItem.addClass 'unloaded'
      $gridItem.fadeIn 'fast'
      return
    ).always ->
      $('.spinner').fadeOut 'fast'
      $('.grid').masonry itemSelector: '.grid-item'
      $('.pagination, .widgets, footer').show()
      return
  else
    $('.widgets, footer').show()
  return
