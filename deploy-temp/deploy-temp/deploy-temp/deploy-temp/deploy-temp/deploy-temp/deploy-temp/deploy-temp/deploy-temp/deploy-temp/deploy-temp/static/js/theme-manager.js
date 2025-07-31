// Multi-Theme Management System for Bolaquent
const themes = {
    'dark': 'GitHub Dark',
    'dracula': 'Dracula',  
    'catppuccin-mocha': 'Catppuccin Mocha',
    'tokyo-night': 'Tokyo Night'
};

function initializeTheme() {
    // Default to dark mode
    const savedTheme = localStorage.getItem('theme');
    const theme = savedTheme || 'dark';
    
    console.log('Initializing theme:', themes[theme] || theme);
    applyTheme(theme);
    updateThemeSelector(theme);
}

function applyTheme(theme) {
    console.log('Applying theme:', themes[theme] || theme);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

function updateThemeSelector(theme) {
    const themeSelector = document.getElementById('theme-selector');
    if (themeSelector) {
        themeSelector.value = theme;
    }
}

function changeTheme(newTheme) {
    console.log('Changing to theme:', themes[newTheme] || newTheme);
    applyTheme(newTheme);
}

// Legacy toggle function for backwards compatibility
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const themeKeys = Object.keys(themes);
    const currentIndex = themeKeys.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themeKeys.length;
    const newTheme = themeKeys[nextIndex];
    applyTheme(newTheme);
    updateThemeSelector(newTheme);
}

// Initialize immediately when script loads
initializeTheme();

// Also initialize on DOM ready as backup
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM ready, re-initializing theme');
    initializeTheme();
});