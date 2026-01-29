const fs = require('fs');

// 1. 检查文件
if (!fs.existsSync('decoder.wasm') || !fs.existsSync('encrypted_input.mp4')) {
    console.error("❌ 缺少文件！");
    process.exit(1);
}

const wasmBuffer = fs.readFileSync('decoder.wasm');
const encryptedData = fs.readFileSync('encrypted_input.mp4');
const len = encryptedData.length;

// === 修复后的 Imports ===
// 先定义核心组件
const memory = new WebAssembly.Memory({ initial: 2048, maximum: 4096 });
const table = new WebAssembly.Table({ initial: 1247, element: 'anyfunc' });

// 基础导入对象
const baseImports = {
    memory: memory,
    table: table
};

// 使用 Proxy 自动填充缺失的函数 (a-q)，但不覆盖 memory 和 table
const proxyA = new Proxy(baseImports, {
    get: (target, prop) => {
        // 1. 如果是 memory 或 table，直接返回实体
        if (prop in target) {
            return target[prop];
        }

        // 2. 否则，动态生成一个“智能函数”
        return (...args) => {
            // 模拟 Date.now()：通常无参调用是在获取时间
            if (args.length === 0) return Date.now();
            
            // 调试日志 (可选，看卡死时在干嘛)
            // console.log(`[Call] a.${String(prop)}`, args);
            
            return 0;
        };
    }
});

const imports = {
    a: proxyA
};

// 测试配置
const configs = [
    { id: '6_fixed', init: 'r', malloc: 's', decrypt: 'y' }, // 之前卡死的组合
    { id: '5_fixed', init: 'r', malloc: 't', decrypt: 'u' }, // 之前无反应的
    { id: '7_blind', init: null, malloc: 's', decrypt: 'y' } // 盲测
];

async function tryConfig(instance, config) {
    const exports = instance.exports;
    console.log(`\n🧪 尝试方案 ${config.id} [Init:${config.init}|Malloc:${config.malloc}|Decrypt:${config.decrypt}]...`);

    try {
        // 1. 初始化
        if (config.init && exports[config.init]) {
            // console.log("   调用初始化...");
            exports[config.init]();
        }

        // 2. 申请内存
        const malloc = exports[config.malloc];
        const ptr = malloc(len);
        // console.log(`   申请内存: ptr=${ptr}`);
        if (ptr === 0) throw new Error("Malloc failed");

        // 3. 写入数据
        const memArray = new Uint8Array(memory.buffer);
        memArray.set(encryptedData, ptr);

        // 4. 解密 (带超时保护)
        console.log("   正在解密 (3秒超时)...");
        const decrypt = exports[config.decrypt];
        
        await new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                console.log("   ⚠️ 解密超时 (可能是死循环)，强制检查结果...");
                resolve(); 
            }, 3000);

            try {
                decrypt(ptr, len);
                clearTimeout(timer);
                resolve();
            } catch (e) {
                clearTimeout(timer);
                reject(e);
            }
        });

        // 5. 检查结果 (FTYP 检测)
        const resultHead = memArray.slice(ptr, ptr + 8);
        
        // MP4 Magic Number: ftyp (0x66 0x74 0x79 0x70)
        // 抖音加密视频通常保持前4字节长度不变，第5-8字节才是 ftyp
        const isFtyp = (resultHead[4] === 0x66 && resultHead[5] === 0x74 && resultHead[6] === 0x79 && resultHead[7] === 0x70);
        
        if (isFtyp) {
            console.log("   🎯 成功！检测到 MP4 头部！");
            const outName = `decrypted_${config.id}.mp4`;
            fs.writeFileSync(outName, memArray.slice(ptr, ptr + len));
            console.log(`   ✅ 文件已保存: ${outName}`);
            return true;
        } else {
            // 简单比对前8字节是否有变化
            const originalHead = encryptedData.slice(0, 8);
            let changed = false;
            for(let i=0; i<8; i++) if(resultHead[i] !== originalHead[i]) changed = true;
            
            if (changed) {
                console.log("   ⚠️ 数据有变化但没检测到 ftyp，仍保存查看。");
                fs.writeFileSync(`decrypted_${config.id}_raw.mp4`, memArray.slice(ptr, ptr + len));
            } else {
                console.log("   ❌ 数据未变化");
            }
        }

    } catch (e) {
        console.log(`   ❌ 错误: ${e.message}`);
    }
    return false;
}

async function run() {
    // 实例化
    const { instance } = await WebAssembly.instantiate(wasmBuffer, imports);
    
    for (const conf of configs) {
        if (await tryConfig(instance, conf)) break;
    }
}

run();