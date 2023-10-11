function rgbToHex(rgb) {
    // Extract RGB components using regex
    let rgbValues = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);

    // Convert RGB to hex
    if (!rgbValues) {
        return rgb; // Return the input if not a valid RGB string
    }

    // Convert each component to hexadecimal and concatenate them
    let hexColor = '#';
    for (let i = 1; i <= 3; i++) {
        let hex = parseInt(rgbValues[i]).toString(16);
        hexColor += hex.length === 1 ? '0' + hex : hex;
    }

    return hexColor;
}

// reload overview page, if at least one of the peers is invalid, every 10 seconds
// to stay updated (backend will at some point know that the peer is valid)
document.addEventListener("DOMContentLoaded", function() {
    let nodeList = document.querySelectorAll('.field-valid_color');
    let foundInvalid = Array.from(nodeList).some(field => {
        return rgbToHex(field.children[0].style.color) === "#e50a0a";
    });

    if (foundInvalid) {
        // reload page every 10 seconds if one of the peers is invalid
        setInterval(function() {
            window.location.reload();
        }, 10000);
    }
});