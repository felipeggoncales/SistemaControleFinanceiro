function abrirFecharMenu() {
    const linha1 = document.getElementById('linha1');
    const linha2 = document.getElementById('linha2');
    const linha3 = document.getElementById('linha3');
    const overlay = document.querySelector('.overlay');
    const itensMenu = document.querySelector('.div-items-menu');

    const linhaDisplay = getComputedStyle(linha1).position;

    if (linhaDisplay === 'static') {
        linha1.style.position = 'absolute';
        linha1.style.transform = 'rotate(-45deg)';
        linha2.style.display = 'none';
        linha3.style.position = 'absolute';
        linha3.style.transform = 'rotate(45deg)';
        overlay.style.display = 'flex';
        setTimeout(()=> {
            if (!overlay.classList.contains('mostrar')) {
                overlay.classList.add('mostrar');
            };
            overlay.classList.replace('esconder','mostrar');
            if (!itensMenu.classList.contains('surgir-menu')) {
                itensMenu.classList.add('surgir-menu');
            };
            itensMenu.style.display = 'flex';
            itensMenu.classList.replace('sumir-menu','surgir-menu');
        },5);
        
    } else {
        linha1.style.position = 'static';
        linha1.style.transform = 'rotate(0deg)';
        linha2.style.display = 'block';
        linha3.style.position = 'static';
        linha3.style.transform = 'rotate(0deg)';
        itensMenu.classList.replace('surgir-menu','sumir-menu');
        overlay.classList.replace('mostrar','esconder');
        setTimeout(()=> {
            if (overlay.classList.contains('esconder')) {
                overlay.style.display = 'none';
            }
        },500);
    };
};


let meta = 1000; // Exemplo de meta
let despesas = 500; // Exemplo de despesas atuais
let porcentagem = (despesas / meta) * 100;

document.querySelector('.wave-container').style.height = `${100 - porcentagem}%`;
document.querySelector('.progress-text p').innerText = `${Math.round(porcentagem)}% do orçamento`;

