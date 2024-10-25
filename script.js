/* Abrir e fecar Menu */

const linha1 = document.getElementById('linha1');
const linha2 = document.getElementById('linha2');
const linha3 = document.getElementById('linha3');
const overlay = document.getElementById('overlay');
const itensMenu = document.querySelector('.div-items-menu');

function abrirFecharMenu() {
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


/* Gráfico de limite de gastos */

var limiteMensal = null;
let gastos = 902 // Variável a ser trocada quando a função de cadastar despesas for implemantada
var porcentagemLimiteConcluido = 75;

const limiteTexto = document.getElementById('porcentagem');
const waves = document.getElementsByClassName('wave');
const loadingBar = document.querySelector('.div-loading');
const porcentagemTexto = document.getElementById('porcentagem');
const limiteMensagem = document.getElementById('limiteMsg');

document.addEventListener('DOMContentLoaded', function() {
    const limiteLocalStorage = localStorage.getItem('limite')
    limiteMensal = limiteLocalStorage ? parseFloat(limiteLocalStorage) : null;

    if (!limiteMensal) {
        limiteTexto.textContent = '?';
        limiteMensagem.textContent = 'Defina seu limite';
    } else {
        alterarGraficoLimite();
    }

    if (porcentagemLimiteConcluido >= 100) {
        porcentagemAcimaDoLimite();
    } else {
        porcentagemAbaixoDoLimite();
    }
})


function alterarGraficoLimite() {
    porcentagemLimiteConcluido = ((gastos / parseInt(limiteMensal))*100).toFixed(1); // Ainda não existe, precisa fazer o banco SQL
    porcentagemTexto.textContent = `${porcentagemLimiteConcluido}%`;
    Array.from(waves).forEach(wave => {
        if (porcentagemLimiteConcluido < 100) {
            wave.style.bottom = `calc(${porcentagemLimiteConcluido}% - 30px)`;
            loadingBar.style.height = `calc(${porcentagemLimiteConcluido}% - 30px)`;
            porcentagemAbaixoDoLimite();
        } else {
            wave.style.bottom = `calc(100% - 30px)`;
            loadingBar.style.height = `calc(100% - 30px)`;
            porcentagemAcimaDoLimite();
        }
    });
}

function porcentagemAcimaDoLimite() {
    Array.from(waves).forEach(wave => {
        wave.style.background = `url(assets/img/wave-acima-limite.png)`;
    });
    loadingBar.style.backgroundColor = `var(--cor-errado)`;
}

function porcentagemAbaixoDoLimite() {
    Array.from(waves).forEach(wave => {
        wave.style.background = `url(assets/img/wave.png)`;
    });
    loadingBar.style.backgroundColor = `var(--cor-princ)`;
}

/* Função para alterar o limite mensal */
const divDefinirLimite = document.getElementById('divDefinirLimite');
const gearButton = document.getElementById('gearButton');
const x = document.getElementById('fecharDivLimite');

gearButton.addEventListener('click', abrirFecharDivLimite);
x.addEventListener('click', abrirFecharDivLimite);
const inputLimite = document.getElementById('limiteInput');
const salvarLimiteButton =  document.getElementById('salvarLimite');
    
function abrirFecharDivLimite() {
    const divDisplay = window.getComputedStyle(divDefinirLimite).display;
    if (divDisplay === 'none') {
        divDefinirLimite.style.display = 'flex';
        inputLimite.value = limiteMensal;
    } else {
        divDefinirLimite.style.display = 'none';
    };
}

salvarLimiteButton.addEventListener('click', function() {
    if (inputLimite.value) {
        limiteMensal = parseInt(inputLimite.value);
        exibirMensagem(limiteMensal);
        storageLimite(limiteMensal);
        alterarGraficoLimite();
    }
})

/* Função para exibir mensagem de limite salvo na tela para o usuário */
const mensagemSalvo = document.getElementById('mensagemLimiteSalvo');
const limiteValor = document.getElementById('limiteValor');
let animacaoAtiva = false;

function exibirMensagem(mensagem) {
    if (animacaoAtiva) return;
    
    animacaoAtiva = true;

    limiteValor.textContent = mensagem;
    mensagemSalvo.classList.add('mensagemSurgir');
    mensagemSalvo.style.display = 'flex';

    setTimeout(() => {
        mensagemSalvo.classList.replace('mensagemSurgir', 'mensagemSumir');
        setTimeout(() => {
            mensagemSalvo.style.display = 'none';
            mensagemSalvo.classList.remove('mensagemSumir');
            animacaoAtiva = false;
        }, 500);
    }, 5000);
}

/* Função para salvar o limite definido pelo usuario no local storage */

function storageLimite(valor) {
    localStorage.setItem('limite', valor)
}