function selectToParagraph(field) {
    const parent = field.parentNode;
    const p = document.createElement("p")
    p.innerText = field.options[field.value].text;
    parent.appendChild(p);
    parent.removeChild(field)
}

function inputToParagraph(field) {
    const parent = field.parentNode;
    const p = document.createElement("p")
    p.innerText = field.value;
    parent.appendChild(p);
    parent.removeChild(field)
}

function inputToCode(field) {
    const parent = field.parentNode;
    const pre = document.createElement("pre")
    pre.innerText = field.value;
    parent.appendChild(pre);
    parent.removeChild(field)
}

document.addEventListener("DOMContentLoaded", function(){
    // TODO do at least the toParagraph transformations in django (read only fields - see without dark reader!)
    selectToParagraph(document.getElementById("id_endpoint"));
    inputToParagraph(document.getElementById("id_name"));
    inputToParagraph(document.getElementById("id_tunnel_ipv4"));
    inputToParagraph(document.getElementById("id_tunnel_ipv6"));
    inputToParagraph(document.getElementById("id_public_key"));
    inputToParagraph(document.getElementById("id_psk"));
    inputToCode(document.getElementById("id_config"));
    document.getElementById("id_tunnel_ipv4").innerText += "/32";
    document.getElementById("id_tunnel_ipv6").innerText += "/128";
});
