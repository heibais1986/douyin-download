
function Window() {
}

window = new Window()
self = window
self.self = window

Location = function Location() {
}
Location.prototype = {
    "ancestorOrigins": {},
    "href": "https://gdtv.cn/channels/2",
    "origin": "https://gdtv.cn",
    "protocol": "https:",
    "host": "gdtv.cn",
    "hostname": "gdtv.cn",
    "port": "",
    "pathname": "/channels/2",
    "search": "",
    "hash": "",
    /*toString() {
        return 'https://gdtv.cn/channels/2'
    }*/

}
location = new Location()

window.location = location

document = {
    toString() {
        return '[object HTMLDocument]'
    },
    location: window.location
}
window.document = document

// 代理监控 proxy: window.location与window.document也需要单独检测
/*function getEnv(proxy_array) {
    for (let i = 0; i < proxy_array.length; i++) {
        handler = `{
            get: function(target, property, receiver) {
                   console.log('方法：get','    对象：${proxy_array[i]}','    属性：',property,'    属性类型：',typeof property,'    属性值类型：',typeof target[property]);
                   return target[property];
            },
            set: function(target, property, value, receiver){
                    console.log('方法：set','    对象：${proxy_array[i]}','    属性：',property,'    属性类型：',typeof property,'    属性值类型：',typeof target[property]);
                    return Reflect.set(...arguments);
            }
        }`;
        eval(`
            try {
                ${proxy_array[i]};
                ${proxy_array[i]} = new Proxy(${proxy_array[i]}, ${handler});
            } catch (e) {
                ${proxy_array[i]} = {};
                ${proxy_array[i]} = new Proxy(${proxy_array[i]}, ${handler});
            }
        `);
    }
}
proxy_array = ['window', 'document', 'location', 'navigator', 'history', 'screen', 'window.document', 'window.location']
getEnv(proxy_array);*/

var fs = require('fs');
var wasm_code = fs.readFileSync('decoder.wasm');

// 检查WASM的导入需求
var module = new WebAssembly.Module(wasm_code);
console.log('WASM Imports:', WebAssembly.Module.imports(module));

// 提供WASM所需的导入
var imports = {
  a: {
    a: () => {},
    b: () => {},
    c: () => {},
    d: () => {},
    e: () => {},
    f: () => {},
    g: () => {},
    h: () => {},
    i: () => {},
    j: () => {},
    k: () => {},
    l: () => {},
    m: () => {},
    n: () => {},
    o: () => {},
    p: () => {},
    q: () => {},
    memory: new WebAssembly.Memory({ initial: 2048, maximum: 2048 }),
    table: new WebAssembly.Table({ initial: 1247, element: 'anyfunc' })
  }
};

WebAssembly.instantiate(wasm_code, imports).then(result => console.log(result))