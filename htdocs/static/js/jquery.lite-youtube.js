/*
 * YouTube Lite Embed - jQuery plugin to embed light-weight YouTube videos
 *
 * Copyright (c) 2012 Amr Tj. Wallas
 *
 * Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License:
 *   http://creativecommons.org/licenses/by-nc-sa/3.0/
 *
 * Project Home:
 *   https://github.com/TjWallas/YouTube-Lite-Embed
 * 
 * Website:
 *    http://tjwallas.weebly.com
 *
 * Version:  1.0-modified
 *
 */

function YTLiteEmbed(liteDivs) {
  liteDivs.each(function() {
    YTLiteInit(this);
  });
  return false;
}

function YTLiteInit(myDiv) {
  var vid = myDiv.id;
  var w = myDiv.style.width;
  var h = myDiv.style.height;

  var img = $(document.createElement('img'));
  img.attr({
    'class': 'lazy',
    'data-original': 'https://i.ytimg.com/vi/'+vid+'/0.jpg',
    'width': w,
    'height': h,
  });
  img.lazyload({
    effect: 'fadeIn',
    threshold: 1000,
  });

  var hoverWorig = 71;
  var hoverHorig = 51;
  var hoverW = (parseInt(w)/2) - (parseInt(hoverWorig)/2);
  var hoverH = (parseInt(h)/2) - (parseInt(hoverHorig)/2);
  var hoverImg = $(document.createElement('img'));
  hoverImg.attr({
    'class': 'lite',
    'style': 'position: absolute;left:'+hoverW+'px;top:'+hoverH+'px;',
    'data-original': 'static/img/youtube-play-button.png',
    'width': hoverWorig,
    'height': hoverHorig,
  });

  hoverImg.lazyload({
    effect: 'fadeIn',
    threshold: 1000,
  });

  var a = $(document.createElement('a'));
  a.href='#';

  $(myDiv).append(a.append(img,hoverImg));

  a.click( function() {
    var div = this.parentNode;
    $(div).fadeOut("fast", function(){
       var iframe = $("<iframe class=\"fadein\" width=\""+div.style.width+"\" height=\""+div.style.height+"\"src=\"https://www.youtube-nocookie.com/embed/"+div.id+"?autohide=0&amp;rel=0&amp;autoplay=1&amp;color=white&amp;html5=1\" allowfullscreen></iframe>").hide();
       $(div).replaceWith(iframe);
       $(iframe).fadeIn(2500,"linear");
    });
    return false;
  });
}

$.fn.YTLite = function() {
    return this.each(function() {
      YTLiteInit(this);
  });
}
