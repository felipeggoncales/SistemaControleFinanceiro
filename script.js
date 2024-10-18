function abrirFecharMenu() {
    const linha1 = document.getElementById('linha1');
    const linha2 = document.getElementById('linha2');
    const overlay = document.querySelector('.overlay');
    const itensMenu = document.querySelector('.div-items-menu');

    const linhaDisplay = getComputedStyle(linha1).position;

    if (linhaDisplay === 'static') {
        linha1.style.position = 'absolute';
        linha1.style.transform = 'rotate(-45deg)';
        linha2.style.position = 'absolute';
        linha2.style.transform = 'rotate(45deg)';
        if (!overlay.classList.contains('mostrar')) {
            overlay.classList.add('mostrar');
        }
        overlay.classList.replace('esconder','mostrar');
        if (!itensMenu.classList.contains('surgir-menu')) {
            itensMenu.classList.add('surgir-menu');
        }
        itensMenu.style.display = 'flex';
        itensMenu.classList.replace('sumir-menu','surgir-menu');
        
    } else {
        linha1.style.position = 'static';
        linha1.style.transform = 'rotate(0deg)';
        linha2.style.position = 'static';
        linha2.style.transform = 'rotate(0deg)';
        itensMenu.classList.replace('surgir-menu','sumir-menu');
        overlay.classList.replace('mostrar','esconder');
    }
}
