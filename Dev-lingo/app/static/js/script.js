// Espera todo o conteúdo da página carregar antes de executar o script
document.addEventListener('DOMContentLoaded', () => {

    // --- Funcionalidade 1: Efeito de Digitação (sem alterações) ---
    const typingElement = document.getElementById('typing-effect');
    const textToType = "BITLINGO uma nova linguagem, agora.";
    let index = 0;

    function type() {
        if (index < textToType.length) {
            typingElement.innerHTML += textToType.charAt(index);
            index++;
            setTimeout(type, 80);
        }
    }
    if (typingElement) {
        type();
    }


    // --- Funcionalidade do Menu Dropdown ---
    const hamburger = document.querySelector('.hamburger-menu');
    // Reintroduzimos esta linha para podermos controlar o menu
    const navMenu = document.querySelector('.main-nav');

    hamburger.addEventListener('click', () => {
        // Alterna a classe 'active' no botão para animar para 'X'
        hamburger.classList.toggle('active');

        // ESTA É A LINHA CHAVE:
        // Alterna a classe 'active' no menu para mostrá-lo ou escondê-lo
        navMenu.classList.toggle('active');
    });

});