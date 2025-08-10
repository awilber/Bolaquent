#!/usr/bin/env node

/**
 * COMPREHENSIVE BOLAQUENT QA TESTING
 * Testing all aspects requested:
 * 1. Homepage Visual Quality
 * 2. Demo Access Methods
 * 3. Core Page Accessibility
 * 4. Theme System
 * 5. Mobile Responsiveness
 */

const { execSync } = require('child_process');
const fs = require('fs');

console.log('🔬 BOLAQUENT COMPREHENSIVE QA TESTING');
console.log('=====================================');
console.log('Timestamp:', new Date().toISOString());

const baseUrl = 'http://localhost:5020';
const results = {
    timestamp: new Date().toISOString(),
    baseUrl: baseUrl,
    tests: {}
};

// Helper function to run curl tests
function runCurlTest(url, description) {
    try {
        console.log(`\n🔗 Testing: ${description}`);
        console.log(`   URL: ${url}`);
        
        const result = execSync(`curl -I "${url}" 2>&1`, { encoding: 'utf-8', timeout: 10000 });
        const success = result.includes('HTTP/1.1 200') || result.includes('HTTP/1.1 302');
        
        console.log(`   Result: ${success ? '✅ SUCCESS' : '❌ FAILED'}`);
        if (!success) {
            console.log(`   Details: ${result.split('\n')[0]}`);
        }
        
        return { success, details: result };
    } catch (error) {
        console.log(`   Result: ❌ FAILED - ${error.message}`);
        return { success: false, details: error.message };
    }
}

// Helper function to test page content
function testPageContent(url, expectedContent, description) {
    try {
        console.log(`\n📄 Testing: ${description}`);
        
        const result = execSync(`curl -s "${url}"`, { encoding: 'utf-8', timeout: 15000 });
        const hasExpectedContent = expectedContent.every(content => result.includes(content));
        
        console.log(`   Result: ${hasExpectedContent ? '✅ SUCCESS' : '❌ FAILED'}`);
        
        // Show what we found
        expectedContent.forEach(content => {
            const found = result.includes(content);
            console.log(`   - "${content}": ${found ? '✅' : '❌'}`);
        });
        
        return { success: hasExpectedContent, content: result };
    } catch (error) {
        console.log(`   Result: ❌ FAILED - ${error.message}`);
        return { success: false, details: error.message };
    }
}

// Test 1: Homepage Visual Quality
console.log('\n🎨 1. HOMEPAGE VISUAL QUALITY TESTING');
console.log('=====================================');

results.tests.homepageVisual = {
    heroBackgrounds: testPageContent(baseUrl, [
        'hero-background',
        'hero-overlay',
        'hero-content'
    ], 'Hero background elements'),
    
    ageTierBadges: testPageContent(baseUrl, [
        'hero-tiers',
        'tier-card'
    ], 'Age tier badges'),
    
    ctaButtons: testPageContent(baseUrl, [
        'btn',
        'call-to-action'
    ], 'Call-to-action buttons'),
    
    themeSelector: testPageContent(baseUrl, [
        'theme-selector',
        'onchange="changeTheme'
    ], 'Theme selector dropdown'),
    
    cssFiles: {
        heroBackgrounds: runCurlTest(`${baseUrl}/static/css/hero-backgrounds.css`, 'Hero backgrounds CSS'),
        additionalThemes: runCurlTest(`${baseUrl}/static/css/additional-themes.css`, 'Additional themes CSS')
    }
};

// Test 2: Demo Access Methods
console.log('\n🚪 2. DEMO ACCESS METHODS TESTING');
console.log('=================================');

results.tests.demoAccess = {
    demoRoute: runCurlTest(`${baseUrl}/demo`, '/demo route'),
    tryRoute: runCurlTest(`${baseUrl}/try`, '/try route'),
    authDemo: runCurlTest(`${baseUrl}/auth/demo`, '/auth/demo route'),
    authQuick: runCurlTest(`${baseUrl}/auth/quick`, '/auth/quick route')
};

// Test bypass login
try {
    console.log('\n🔓 Testing bypass login...');
    execSync(`curl -X POST -d "username=bypass" -c cookies.txt -s "${baseUrl}/auth/login" > /dev/null`, { timeout: 10000 });
    const dashboardTest = runCurlTest(`${baseUrl}/learning/dashboard`, 'Dashboard access after bypass login');
    results.tests.demoAccess.bypassLogin = dashboardTest;
    
    // Clean up
    try { fs.unlinkSync('cookies.txt'); } catch (e) {}
} catch (error) {
    console.log('   Bypass login: ❌ FAILED - ' + error.message);
    results.tests.demoAccess.bypassLogin = { success: false, details: error.message };
}

// Test 3: Core Page Accessibility
console.log('\n📋 3. CORE PAGE ACCESSIBILITY TESTING');
console.log('=====================================');

results.tests.pageAccessibility = {
    homepage: testPageContent(baseUrl, ['<title>Bolaquent - Vocabulary Learning</title>'], 'Homepage title'),
    loginPage: testPageContent(`${baseUrl}/auth/login`, ['<title>Login - Bolaquent</title>'], 'Login page title'),
    errorPage: testPageContent(`${baseUrl}/nonexistent-page`, ['<title>Page Not Found - Bolaquent</title>'], '404 error page')
};

// Test dashboard accessibility (requires session)
try {
    execSync(`curl -X POST -d "username=bypass" -c cookies2.txt -s "${baseUrl}/auth/login" > /dev/null`, { timeout: 10000 });
    results.tests.pageAccessibility.dashboard = testPageContent(`${baseUrl}/learning/dashboard`, [
        '<title>Dashboard - Bolaquent</title>',
        'hero-background'
    ], 'Dashboard with hero background');
    try { fs.unlinkSync('cookies2.txt'); } catch (e) {}
} catch (error) {
    results.tests.pageAccessibility.dashboard = { success: false, details: error.message };
}

// Test 4: Theme System
console.log('\n🎭 4. THEME SYSTEM TESTING');
console.log('==========================');

results.tests.themeSystem = {
    dataTheme: testPageContent(baseUrl, [
        'data-theme="dark"',
        'class="theme-educational"'
    ], 'Dark theme data attributes'),
    
    themeOptions: testPageContent(baseUrl, [
        'value="dark"',
        'value="dracula"',
        'value="catppuccin-mocha"',
        'value="tokyo-night"'
    ], 'Multiple theme options'),
    
    themeManager: runCurlTest(`${baseUrl}/static/js/theme-manager.js`, 'Theme manager JavaScript')
};

// Test 5: Mobile Responsiveness
console.log('\n📱 5. MOBILE RESPONSIVENESS TESTING');
console.log('===================================');

// Test mobile meta tags
const mobileMetaTags = testPageContent(baseUrl, [
    'width=device-width',
    'apple-mobile-web-app-capable',
    'mobile-web-app-capable'
], 'Mobile viewport meta tags');

// Test mobile CSS media queries
const mobileCss = testPageContent(`${baseUrl}/static/css/hero-backgrounds.css`, [
    '@media (max-width: 768px)',
    '@media (max-width: 480px)'
], 'Mobile CSS media queries');

results.tests.mobileResponsiveness = {
    metaTags: mobileMetaTags,
    mediaQueries: mobileCss
};

// Generate Summary
console.log('\n📊 COMPREHENSIVE QA RESULTS SUMMARY');
console.log('===================================');

let totalTests = 0;
let passedTests = 0;

function countResults(obj, path = '') {
    for (const [key, value] of Object.entries(obj)) {
        if (value && typeof value === 'object' && value.success !== undefined) {
            totalTests++;
            if (value.success) passedTests++;
            console.log(`${value.success ? '✅' : '❌'} ${path}${key}`);
        } else if (value && typeof value === 'object') {
            countResults(value, `${path}${key}.`);
        }
    }
}

countResults(results.tests);

const passRate = Math.round((passedTests / totalTests) * 100);
console.log(`\n🎯 FINAL SCORE: ${passedTests}/${totalTests} tests passed (${passRate}%)`);

// Overall Assessment
if (passRate >= 90) {
    console.log('🌟 EXCELLENT: Bolaquent app is performing exceptionally well!');
} else if (passRate >= 75) {
    console.log('✅ GOOD: Bolaquent app is working well with minor issues.');
} else if (passRate >= 60) {
    console.log('⚠️  FAIR: Bolaquent app has some issues that need attention.');
} else {
    console.log('❌ POOR: Bolaquent app has significant issues requiring immediate attention.');
}

// Save detailed results
const reportFile = `bolaquent-qa-report-${Date.now()}.json`;
fs.writeFileSync(reportFile, JSON.stringify(results, null, 2));
console.log(`\n📋 Detailed report saved: ${reportFile}`);

// Additional recommendations
console.log('\n💡 RECOMMENDATIONS:');
console.log('===================');

if (results.tests.homepageVisual.heroBackgrounds.success) {
    console.log('✅ Hero backgrounds are properly implemented');
} else {
    console.log('❌ Consider checking hero-backgrounds.css implementation');
}

if (results.tests.demoAccess.authDemo.success && results.tests.demoAccess.authQuick.success) {
    console.log('✅ Demo access methods are working correctly');
} else {
    console.log('❌ Some demo access routes may need debugging');
}

if (results.tests.themeSystem.dataTheme.success && results.tests.themeSystem.themeOptions.success) {
    console.log('✅ Theme system is fully functional');
} else {
    console.log('❌ Theme system may need additional work');
}

if (results.tests.mobileResponsiveness.metaTags.success && results.tests.mobileResponsiveness.mediaQueries.success) {
    console.log('✅ Mobile responsiveness is properly implemented');
} else {
    console.log('❌ Mobile responsiveness may need improvement');
}

console.log('\n✨ QA Testing Complete!');
console.log('Please test http://localhost:5020 in your browser to verify visual quality.');