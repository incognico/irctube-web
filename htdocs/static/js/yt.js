// Funktion, welche prüft, ob du ein bestimmtes Element gerade siehst. Hier brauchst du absolut nichts ändern
function isScrolledIntoView(elem) {
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return ((elemBottom >= docViewTop) && (elemTop <= docViewBottom));
}

// Funktion welche beim Scrollen abgefeuert wird und die obige Funktion ausführt
function checkAndLoad(){
    if(isScrolledIntoView($('.footer'))){ // wenn dein div.footer zu sehen ist, wird ein Popup erscheinen
        alert('BIN UNTEN'); // an dieser Stelle sollte der Ajax Kram rein, der später weitere Videos nachlädt
    }
}

// Dieser Part führt nach dem Laden der Seite die obige Funktion aus und reagiert sonst nur auf das scroll Event
$(document).ready(function(){
    checkAndLoad();
    $(window).scroll(function(){
        checkAndLoad();
    });
});

