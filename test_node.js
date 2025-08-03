
    const fs = require('fs');
    
    // Read the JavaScript file
    const jsCode = fs.readFileSync('lib/js/douyin.js', 'utf8');
    
    try {
        // Execute the JavaScript code
        eval(jsCode);
        
        console.log('JavaScript file loaded successfully');
        
        // Test functions
        const testParams = "device_platform=webapp&aid=6383&channel=channel_pc_web";
        const testUA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";
        
        // Test se function
        try {
            const seResult = se('123', 5, '0');
            console.log('se function result:', seResult);
        } catch (e) {
            console.log('se function error:', e.message);
        }
        
        // Test rc4_encrypt function
        try {
            const rc4Result = rc4_encrypt('test', 'key');
            console.log('rc4_encrypt function result:', rc4Result);
        } catch (e) {
            console.log('rc4_encrypt function error:', e.message);
        }
        
        // Test sign_datail function
        try {
            const signResult = sign_datail(testParams, testUA);
            console.log('sign_datail function result:', JSON.stringify(signResult));
        } catch (e) {
            console.log('sign_datail function error:', e.message);
        }
        
    } catch (e) {
        console.log('Error loading JavaScript:', e.message);
        console.log('Stack:', e.stack);
    }
    