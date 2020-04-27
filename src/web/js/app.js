/*jshint esversion: 8 */

let page_cursor = 0;
let page_current = 0;
let splitter = '\n';
let text_tmp = '';
let submit_enable = false;
let menu_open = true;
let on_edit = true;
const max_text_size = 200;
let config = {};
let options = {};
let converter = {};
let header = {};


const config_ids = {
    'menu': 'setting-default-menu',
    'font-family': 'setting-font-family',
    'font-size': 'setting-font-size',
};

let config_items = [
    'menu',
    'font-family',
    'font-size',
];


const option_converted = {
    'menu': {
        true: 'on',
        false: 'off',
    },
    'font-family': {
        'sans-serif': 'sans-serif',
        'serif': 'serif',
        'monospace': 'monospace',
    },
    'font-size': {
        'small': 'small',
        'medium': 'medium',
        'large': 'large',
    },
};

const option_reversed = {
    'menu': {
         'on':true,
         'off':false,
    },
    'font-family': {
         'sans-serif':'sans-serif',
         'serif':'serif',
         'monospace':'monospace',
    },
    'font-size': {
         'small':'small',
         'medium':'medium',
         'large':'large',
    },
};

let header_items = [
    'title',
    'author',
    'created_at',
    'last_updated',
];



// interface with eel

async function getPageContent(page_number){
    let res = await eel.get_page(page_number)();
    return res;
}

async function getTotalPageSize(){
    let res = await eel.get_page_size()();
    document.getElementById('page-total').textContent = res;
}

async function getTitle(){
    let res = await eel.get_title()();
    document.getElementById('text-title').textContent = res;
}

async function saveText(text){
    let muted = $('#play-SE').hasClass('muted');
    let res = await eel.save_text(text)();
    if(res){
        updateTimestamps(res);
        if(!muted){
            playSound();
        }
        createNewPage();
    }
    return res;
}

async function openNewFile(){
    let res = await eel.open_new_file()();
    document.getElementById('text-title').textContent = res;
    page_cursor = 0;
    page_current = 0;
    resetInputText();
    setPageTotal();
    setPageCurrent();
    setPlaceholder();
    loadHeader();
}

async function openFile(){
    let res = await eel.change_file()();
    if(res){
        document.getElementById('text-title').textContent = res.title;
        resetInputText();
        page_current = res.current_page;
        page_cursor = res.current_page;
        setPageTotal();
        setPageCurrent();
        loadHeader();
    }else{
        alert('Failed to read file.');
    }
    $('#open-file').removeClass('disabled');
}

async function getInfo(){
    let res = await eel.get_stats()();
    let text_count = document.getElementById('manuscript').value.split(splitter).join('').length;
    // document.getElementById('fileinfo-character-size').innerText = res.text_size + text_count;
    // document.getElementById('fileinfo-block-size').innerText = res.page_size + 1;
    // document.getElementById('fileinfo-path').innerText = res.fullpath;

    /*
    var display_text = 
        '******Inforamtion******\n' +
        'title:' + res.title + '\n\n' + 
        'text length: ' + (res.text_size + text_count) + ' characters.\n' +
        'block length: ' + (res.page_size + 1) + ' blocks.\n\n' +
        'path: \n' + res.fullpath + '\n';
    alert(display_text);
    */
}

async function getConfig(){
    let res = await eel.get_config()();
    config = res; // global
    return res;
}

async function getOptions(){
    let res = await eel.get_config_options()();
    options = res;
    return res;
}

async function saveConfig(){
    let res = await eel.save_config(getOptionSelected())();
    config = res;
    reflectSelected();
    reflectConfig();
    return res;
}

async function loadHeader(){
    let res = await eel.get_header()();
    header = res;
    reflectHeader();
    return res;
}

async function changeFileInfo(){
    let title = document.getElementById('edit-property-title').value;
    let author = document.getElementById('edit-property-author').value;
    let res = await eel.change_fileinfo(title, author)();
    header = res;
    reflectHeader();
    return res;
}

async function preview(){
    let res = await eel.preview()();
    window.open('preview.html', 'preview');
    return res;
}

async function exportText(){
    let res = await eel.export_file()();
    return res;
}


// normal funcitons

function disableIcon(elementId){
    var target = $('#' + elementId);
    target.removeClass('clickable');
    target.addClass('disabled');
    target.css('color', 'lightgrey');
}

function enableIcon(elementId){
    var target = $('#' + elementId);
    target.removeClass('disabled');
    target.addClass('clickable');
    target.css('color', '');
}

function disableIcons(elementIds){
    elementIds.forEach(function(element){
        disableIcon(element);
    });
}
function enableIcons(elementIds){
    elementIds.forEach(function(element){
        enableIcon(element);
    });
}

function enableSubmit(){
    $('#save-text').prop('disabled', false);
    enableIcon('save-text');
    submit_enable = true;
    document.getElementById('save-text').style.background = '';
    document.getElementById('save-text').style.cursor = '';
    document.getElementById('manuscript').style.background = '';
}

function disableSubmit(change_bg){
    if(typeof change_bg === 'undefined'){
        change_bg = true;
    }
    $('#save-text').prop('disabled', true);
    disableIcon('save-text');
    submit_enable = false;
    document.getElementById('save-text').style.background = 'lightgray';
    document.getElementById('save-text').style.cursor = 'not-allowed';
    if(change_bg){
        document.getElementById('manuscript').style.background = 'whitesmoke';
    }
}

function setPageTotal(){
    document.getElementById('page-total').textContent = page_cursor + 1;
}

function setPageCurrent(){
    document.getElementById('page-current').textContent = page_current + 1;
    if(page_current == page_cursor){
        disableIcons(['page-next', 'page-last']);
        on_edit = true;
    }else{
        enableIcons(['page-next', 'page-last']);
        disableSubmit();
        on_edit = false;
    }
    if(page_current == 0){
        disableIcons(['page-first', 'page-previous']);
    }else{
        enableIcons(['page-first', 'page-previous']);
    }
    $('#manuscript').prop('readonly', page_current != page_cursor);
    
    if(on_edit){
        document.getElementById('manuscript').style.background = '';
    }
    updateTextCount();
}

function updateTextCount(){
    var text = document.getElementById('manuscript').value;
    var count = text.split(splitter).join('').length;
    var target = document.getElementById('current-count');
    target.textContent = count;
    if(count > 0 && count <= max_text_size){
        target.style.color = '';
        target.style.fontWeight = '';
        if(on_edit){
            enableSubmit();
        }
    }else{
        if(count > max_text_size){
            target.style.color = 'red';
            target.style.fontWeight = 'bold';
        }
        disableSubmit(false);
    }
}

function initTextCount(){
    document.getElementById('manuscript').value = '';
    document.getElementById('current-count').textContent = '0';
}

function saveInputText(){
    if(submit_enable){
        text_tmp = document.getElementById('manuscript').value;
    }
}

function clearInputText(){
    text_tmp = '';
}

function createNewPage(){
    initTextCount();
    clearInputText();
    page_cursor += 1;
    page_current += 1;
    setPageTotal();
    setPageCurrent();
}

function loadInputText(){
    document.getElementById('manuscript').value = text_tmp;
    updateTextCount();
}

function resetInputText(){
    document.getElementById('manuscript').value = '';
    updateTextCount();
}

function openPage(page_number){
    // preprocess
    if(page_number < 0) return false;
    if(page_number > page_cursor) return false;
    if(page_current == page_cursor){
        saveInputText();
    }

    // main 
    if(page_number == page_cursor){
        loadInputText();
        resizeTextArea(5);
    }else{
        var res = getPageContent(page_number);
        res.then(function(value){
            document.getElementById('manuscript').value = value;
            updateTextCount();
            resizeTextArea();
        });
    }

    // postprocess
    page_current = page_number;
    setPageCurrent();
}

// resize function

function resizeWindow(){
    var main = document.getElementById('main-area');
    if(window.innerWidth < 768){
        if(menu_open){
            main.style.height = window.innerHeight - $('.menu').height() + 'px';
        }else{
            main.style.height = window.innerHeight + 'px';
        }
    }else{
        main.style.height = '100%';
    }
}

function resizeTextArea(size){
    var target = $('#manuscript');

    if(typeof size !== undefined){
        target.attr('rows', size);
        return;
    }

    var element = target.get(0);
    var height = Number(target.attr('rows'));

    while(element.scrollHeight > element.offsetHeight){
        height += 1;
        target.attr('rows', height);
    }
}

// config

function loadConfig(){
    converter = getOptionStructure();
    getOptions();
    var loading = getConfig();
    loading.then(function(){
        reflectSelected();
        reflectConfig();
    });
}


function setFontFamily(font){
    document.getElementById('manuscript').style.fontFamily = font;
}

function setFontSize(size){
    document.getElementById('manuscript').style.fontSize = size;
}

function getOptionStructure(){
    var res = {};
    $('.setting-item-select').each(function(index, element){
        res[element.id] = convertOptions(element);
    });
    $('.setting-item-input').each(function(index, element){
        res[element.id] = {};
    });
    return res;
}

function convertOptions(element){
    var res = {};
    $.each(element.options, function(key, value){
        res[value.value] = key;
    });
    return res;
}

function reflectSelected(){
    var target;
    var selected_index;
    $.each(config, function(key,value){
        if(config_ids[key]){
            target = document.getElementById(config_ids[key]);
            if(key == 'default-file-name' || key == 'directory'){
                target.value = value;
            }else{
                console.info(key);
                selected_index = converter[config_ids[key]][option_converted[key][value]];
                target.options[selected_index].selected = true;
            }
        }
    });
}

function getOptionSelected(){
    let result = {};
    config_items.forEach(function(key){
        if(key == 'default-file-name' || key == 'directory'){
            result[key] = document.getElementById(config_ids[key]).value;
        }else{
            result[key] = option_reversed[key][document.getElementById(config_ids[key]).value];
        }
    });
    return result;
}

function reflectConfig(){
    $.each(config, function(key,value){
        switch (key) {
            case 'font-family':
                setFontFamily(value);
                break;
            case 'font-size':
                console.log(value);
                setFontSize(value);
                break;
            default:
                break;
        }
    });
}

function reflectHeader(){
    console.log(header);
    let title = (typeof header.title !== 'undefined' && header.title.length > 0) ? header.title : 'untitled';
    let author = (typeof header.author !== 'undefined') ? header.author : '';
    let created_at = (header.created_at) ? header.created_at : '-';
    let last_updated = (header.last_updated) ? header.last_updated : '-';
    document.getElementById('text-title').innerText = title;
    document.getElementById('fileinfo-title').innerText = title;
    document.getElementById('edit-property-title').value = title;
    document.getElementById('fileinfo-author').innerText = author;
    document.getElementById('edit-property-author').value = author;
    document.getElementById('fileinfo-created-at').innerText = created_at;
    document.getElementById('fileinfo-last-updated').innerText = last_updated;
}

function setPlaceholder(content){
    if(typeof content === 'undefined'){
        content = 'Jot down your thoughts.';
    }

    $('#manuscript').attr('placeholder', content);
}

function updateTimestamps(res){
    header.created_at = res.created_at;
    header.last_updated = res.updated_at;
}

function changeAppTitle(title){

}

// sound

function playSound(){
    document.getElementById('carriage-return').currentTime = 0;
    document.getElementById('carriage-return').play();
}

function toggleMuted(){
    let target = $('#play-SE');
    if(target.hasClass('muted')){
        target.removeClass('muted');
        target.attr('title', 'Sound Effect: ON');
        target[0].innerText = 'volume_up';
    }else{
        target.addClass('muted');
        target.attr('title', 'Sound Effect: OFF');
        target[0].innerText = 'volume_off';
    }

}




