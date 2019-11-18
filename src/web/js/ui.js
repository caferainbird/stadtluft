// menu

$(document).on('click', '#menu-open', function(event){
    menu_open = true;
    resizeWindow();
    $('.menu').slideDown('fast',function(){
        $('#menu-open').fadeOut();
        resizeWindow();
    });
});

$(document).on('click', '#menu-close', function(event){
    $('#menu-open').fadeIn();
    $('.menu').slideUp('fast', function(){
        menu_open = false;
        resizeWindow();
    });
});

// file 

$(document).on('keyup', '.text-space', function(event){
    saveInputText();
    updateTextCount();
});

$(document).on('click', '#new-file', function(event){
    var res = openNewFile();
});

$(document).on('click', '#open-file', function(event){
    if(! $('#open-file').hasClass('disabled')){
        $('#open-file').addClass('disabled');
        var res = openFile();
    }
});

$(document).on('click', '#save-text', function(event){
    if(! submit_enable){
        console.log('submit failed');
        return false;
    }
    var text = document.getElementById('manuscript').value;
    saveText(text)
});

$(document).on('click', '#view-in-browser', function(event){
    console.log('preview');
    preview();
});

$(document).on('click', '#export-file', function(event){
    console.log('export');
    exportText();
});

// page

$(document).on('click', '#page-first', function(event){
    console.log('jumb first-page');
    openPage(0);
});

$(document).on('click', '#page-last', function(event){
    console.log('jumb last-page');
    openPage(page_cursor);
});

$(document).on('click', '#page-previous', function(event){
    console.log('page -1');
    openPage(page_current - 1);
});

$(document).on('click', '#page-next', function(event){
    console.log('page +1');
    openPage(page_current + 1);
});

// config

$(document).on('click', '#open-info', function(event){
    getInfo();
    reflectHeader();
    $('[data-remodal-id="fileinfo"]').remodal().open();
});

$(document).on('click', '#open-help', function(event){
    $('[data-remodal-id="about"]').remodal().open();
});

$(document).on('click', '#open-config', function(event){
    reflectSelected();
    $('[data-remodal-id="config"]').remodal().open();
});

$(document).on('click', '#edit-property', function(event){
    reflectHeader();
    $('[data-remodal-id="property"]').remodal().open();
});

$(document).on('click', '#save-config', function(event){
    var res = saveConfig();
    res.then(function(){
        reflectConfig();
        $('[data-remodal-id="config"]').remodal().close();
    });
});

$(document).on('click', '#save-fileinfo', function(event){
    var res = changeFileInfo();
    res.then(function(){
        $('[data-remodal-id="property"]').remodal().close();
    });
});


$(document).on('keydown', '#manuscript', function(event){
    if(event.shiftKey){
        if(event.keyCode === 13){
            $('#save-text')[0].click();
            return false;
        }
    }

    if(event.ctrlKey){
        if(event.keyCode === 13){
            $('#save-text')[0].click();
            return false;
        }
    }
});


$(document).on('click', '#play-SE', function(event){
    toggleMuted();
});

$(function(){
    var timer = null;
    $(window).on('resize',function() {
        clearTimeout(timer);
        timer = setTimeout(function() {
            resizeWindow();
            clearTimeout(timer);
        }, 40 );
    });
});

// initialize

setPageCurrent();
updateTextCount();
resizeWindow();
loadConfig();


