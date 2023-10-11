document.addEventListener("DOMContentLoaded", function(){
    // hide psk field, until checkbox gets checked
    document.querySelector(".field-psk").style.display = "none";

    // create new html element for private key
    const djangoField_privateKey = document.getElementById("id_private_key");
    const div_privateKey = djangoField_privateKey.parentNode;
    const p_privateKey = document.createElement("p")

    // generate wireguard keypair
    let wg = window.wireguard.generateKeypair();
    p_privateKey.innerText = wg.privateKey;
    delete wg.privateKey;
    document.getElementById("id_public_key").value = wg.publicKey;
    delete wg.publicKey;

    // add paragraph and delete original django field for private key
    div_privateKey.appendChild(p_privateKey);
    div_privateKey.removeChild(djangoField_privateKey)

    // event listener for the "configure psk" checkbox
    document.getElementById("id_configure_psk").addEventListener('change', e => {
        if (e.target.checked) {
            document.getElementById("id_psk").value = window.wireguard.generatePSK();
            document.querySelector(".field-psk").style.display = "block";
            document.getElementById("id_psk").readOnly = true;
        } else {
            document.querySelector(".field-psk").style.display = "none";
        }
    });
});

