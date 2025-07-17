//Espera o HTML carregar antes de rodar o script
document.addEventListener('DOMContentLoaded', () => {

    //Efeito de Digitação
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
    //Inicia o efeito se o elemento existir
    if (typingElement) {
        type();
    }


    //Menu Dropdown 
    const hamburger = document.querySelector('.hamburger-menu');
    //Controlar o menu
    const navMenu = document.querySelector('.main-nav');

    // Ao clicar no ícone do hamburguer
    hamburger.addEventListener('click', () => {
        // Alterna a classe 'active' para animar o ícone e mostrar/esconder o menu
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

});