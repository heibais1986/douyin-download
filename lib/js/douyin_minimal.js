// Minimal version of douyin.js with only essential functions

function rc4_encrypt(plaintext, key) {
    var s = [];
    for (var i = 0; i < 256; i++) {
        s[i] = i;
    }
    var j = 0;
    for (var i = 0; i < 256; i++) {
        j = (j + s[i] + key.charCodeAt(i % key.length)) % 256;
        var temp = s[i];
        s[i] = s[j];
        s[j] = temp;
    }

    var i = 0;
    var j = 0;
    var cipher = [];
    for (var k = 0; k < plaintext.length; k++) {
        i = (i + 1) % 256;
        j = (j + s[i]) % 256;
        var temp = s[i];
        s[i] = s[j];
        s[j] = temp;
        var t = (s[i] + s[j]) % 256;
        cipher.push(String.fromCharCode(s[t] ^ plaintext.charCodeAt(k)));
    }
    return cipher.join('');
}

function se(str, length, padChar) {
    str = String(str);
    while (str.length < length) {
        str = padChar + str;
    }
    return str;
}

function generate_random_str() {
    var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var result = '';
    for (var i = 0; i < 16; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

function generate_rc4_bb_str() {
    var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var result = '';
    for (var i = 0; i < 16; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// Base64 encode function for JScript compatibility
function base64_encode(str) {
    var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    var result = '';
    var i = 0;
    
    while (i < str.length) {
        var a = str.charCodeAt(i++);
        var b = i < str.length ? str.charCodeAt(i++) : 0;
        var c = i < str.length ? str.charCodeAt(i++) : 0;
        
        var bitmap = (a << 16) | (b << 8) | c;
        
        result += chars.charAt((bitmap >> 18) & 63);
        result += chars.charAt((bitmap >> 12) & 63);
        result += i - 2 < str.length ? chars.charAt((bitmap >> 6) & 63) : '=';
        result += i - 1 < str.length ? chars.charAt(bitmap & 63) : '=';
    }
    
    return result;
}

// Simplified sign functions
function sign_datail(params, ua) {
    var now = new Date();
    var timestamp = Math.floor(now.getTime() / 1000);
    var random_str = generate_random_str();
    
    // Simple signature generation
    var sign_str = params + '&timestamp=' + timestamp + '&random=' + random_str;
    var signature = base64_encode(sign_str).substring(0, 32);
    
    var result = {};
    result['X-Bogus'] = signature;
    result['timestamp'] = timestamp;
    result['random_str'] = random_str;
    
    return result;
}

function sign_reply(params, ua) {
    return sign_datail(params, ua);
}

function sign(params, ua) {
    return sign_datail(params, ua);
}