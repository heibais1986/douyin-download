const fs = require('fs');

// 1. 检查文件
if (!fs.existsSync('decoder.wasm') || !fs.existsSync('encrypted_input.mp4')) {
    console.error("❌ 缺少文件！请确保目录包含 'decoder.wasm' 和 'encrypted_input.mp4'");
    process.exit(1);
}

const wasmBuffer = fs.readFileSync('decoder.wasm');
const encryptedData = fs.readFileSync('encrypted_input.mp4');
const len = encryptedData.length;

// 模拟导入对象
const imports = {
    a: {
        a: () => 0, b: () => 0, c: () => 0, d: () => 0,
        e: () => 0, f: () => 0, g: () => 0, h: () => 0,
        i: () => 0, j: () => 0, k: () => 0, l: () => 0,
        m: () => 0, n: () => 0, o: () => 0, p: () => 0, q: () => 0,
        memory: new WebAssembly.Memory({ initial: 2048, maximum: 4096 }),
        table: new WebAssembly.Table({ initial: 1247, element: 'anyfunc' })
    }
};

// 定义所有可能的组合
// Init candidates: [null, 'w', 'r'] (可能是 w 或 r，也可能不需要)
// Malloc candidates: ['t', 's']
// Decrypt candidates: ['u', 'y']
const configs = [
    // 优先尝试带初始化的方案 (w 看起来最像 init)
    { init: 'w', malloc: 't', decrypt: 'u' },
    { init: 'w', malloc: 's', decrypt: 'y' },
    { init: 'w', malloc: 't', decrypt: 'y' },
    { init: 'w', malloc: 's', decrypt: 'u' },
    
    // 尝试 r 作为初始化
    { init: 'r', malloc: 't', decrypt: 'u' },
    { init: 'r', malloc: 's', decrypt: 'y' },

    // 尝试无初始化 (直接调用)
    { init: null, malloc: 's', decrypt: 'u' },
    { init: null, malloc: 't', decrypt: 'y' },
];

async function tryConfig(instance, config, idx) {
    const exports = instance.exports;
    const label = `方案 ${idx + 1} [Init:${config.init || '无'} | Malloc:${config.malloc} | Decrypt:${config.decrypt}]`;
    
    console.log(`\n🧪 正在尝试 ${label}...`);

    try {
        // 1. 初始化
        if (config.init && exports[config.init]) {
            exports[config.init](); // 调用初始化函数
        }

        // 2. 申请内存
        const malloc = exports[config.malloc];
        if (typeof malloc !== 'function') throw new Error("Malloc不是函数");
        
        const ptr = malloc(len);
        if (ptr === 0) throw new Error("Malloc 返回了空指针");
        
        // 3. 写入数据
        const memArray = new Uint8Array(imports.a.memory.buffer);
        memArray.set(encryptedData, ptr);

        // 4. 解密
        const decrypt = exports[config.decrypt];
        if (typeof decrypt !== 'function') throw new Error("Decrypt不是函数");
        
        decrypt(ptr, len); // 原地解密

        // 5. 验证结果 (简单检查：MP4头通常是 00 00 00 ... ftyp)
        // 解密后的前4个字节通常代表长度，第5-8字节是 'ftyp' (0x66747970)
        // 或者至少不应该和原文一模一样
        const resultHead = memArray.slice(ptr, ptr + 8);
        const originalHead = encryptedData.slice(0, 8);
        
        let isDifferent = false;
        for(let i=0; i<8; i++) {
            if (resultHead[i] !== originalHead[i]) isDifferent = true;
        }

        if (!isDifferent) {
            console.log(`   ⚠️ 警告: 数据未发生变化，该组合可能无效。`);
        } else {
            console.log(`   ✅ 成功！数据已发生变化。`);
            
            // 保存结果
            const outputName = `decrypted_${idx+1}.mp4`;
            const decryptedData = memArray.slice(ptr, ptr + len);
            fs.writeFileSync(outputName, decryptedData);
            console.log(`   🎉 已保存文件: ${outputName}`);
            console.log(`   👉 请尝试播放此文件！`);
            return true; // 成功
        }

    } catch (e) {
        console.log(`   ❌ 失败: ${e.message.split('\n')[0]}`);
    }
    return false;
}

async function run() {
    console.log("🚀 开始全自动破解...");
    
    // 对每个配置，我们需要重新实例化 WASM，以防内存状态污染
    for (let i = 0; i < configs.length; i++) {
        // 重新创建 imports (清空内存)
        const currentImports = {
            a: { ...imports.a, 
                 memory: new WebAssembly.Memory({ initial: 2048, maximum: 4096 }),
                 table: new WebAssembly.Table({ initial: 1247, element: 'anyfunc' })
            }
        };

        const { instance } = await WebAssembly.instantiate(wasmBuffer, currentImports);
        
        const success = await tryConfig(instance, configs[i], i);
        if (success) {
            console.log("\n✅✅✅ 破解完成！请查看生成的 mp4 文件。");
            return;
        }
    }
    console.log("\n❌ 所有方案均失败。可能需要更深入的 JS 逆向。");
}

run();