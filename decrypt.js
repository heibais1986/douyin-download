const fs = require('fs');

// 1. 读取 WASM 文件
// 确保 'decoder.wasm' 在同一目录下
if (!fs.existsSync('decoder.wasm')) {
    console.error("❌ 错误: 找不到 decoder.wasm 文件！");
    process.exit(1);
}
const wasmBuffer = fs.readFileSync('decoder.wasm');

// 2. 模拟空导入对象 (只要不报错就行)
const imports = {
    a: {
        a: () => {}, b: () => {}, c: () => {}, d: () => {},
        e: () => {}, f: () => {}, g: () => {}, h: () => {},
        i: () => {}, j: () => {}, k: () => {}, l: () => {},
        m: () => {}, n: () => {}, o: () => {}, p: () => {}, q: () => {},
        memory: new WebAssembly.Memory({ initial: 2048, maximum: 4096  }),
        table: new WebAssembly.Table({ initial: 1247, element: 'anyfunc' })
    }
};

async function run() {
    try {
        // 3. 实例化 WASM
        const { instance } = await WebAssembly.instantiate(wasmBuffer, imports);
        const exports = instance.exports;

        console.log("✅ WASM 加载成功！");

        // 4. 定义候选函数 (方案 A: t + u)
        const malloc = exports.t;  // 内存分配函数
        const decrypt = exports.u; // 解密函数

        // 读取加密文件
        const inputPath = 'encrypted_input.mp4'; 
        if (!fs.existsSync(inputPath)) {
            console.log("❌ 错误: 找不到加密视频文件！");
            console.log("请将您下载的乱码视频重命名为 'encrypted_input.mp4' 并放在同目录下。");
            return;
        }
        
        console.log(`正在读取文件: ${inputPath}`);
        const fileData = fs.readFileSync(inputPath);
        const len = fileData.length;

        console.log(`文件大小: ${len} 字节，正在申请 WASM 内存...`);
        
        // A. 申请内存
        const ptr = malloc(len);
        console.log(`内存申请成功，地址: ${ptr}`);

        // B. 写入数据
        const memArray = new Uint8Array(imports.a.memory.buffer);
        memArray.set(fileData, ptr);

        console.log("正在解密...");
        
        // C. 解密
        decrypt(ptr, len);

        // D. 读取数据
        const decryptedData = memArray.slice(ptr, ptr + len);

        // E. 保存
        const outputPath = 'decrypted_output.mp4';
        fs.writeFileSync(outputPath, decryptedData);
        console.log(`✅ 解密完成！已保存为: ${outputPath}`);

    } catch (e) {
        console.error("❌ 运行出错:", e);
    }
}

run();