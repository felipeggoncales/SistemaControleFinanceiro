
function abrirFecharMenu() {
    const linha1 = document.getElementById('linha1');
    const linha2 = document.getElementById('linha2');

    const linhaDisplay = getComputedStyle(linha1).position;
    if (linhaDisplay === 'static') {
        linha1.style.position = 'absolute';
        linha1.style.transform = 'rotate(-45deg)';
        linha2.style.position = 'absolute';
        linha2.style.transform = 'rotate(45deg)';
    } else {
        linha1.style.position = 'static';
        linha1.style.transform = 'rotate(0deg)';
        linha2.style.position = 'static';
        linha2.style.transform = 'rotate(0deg)';
    }
}