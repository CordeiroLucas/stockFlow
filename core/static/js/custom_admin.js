document.addEventListener("DOMContentLoaded", function() {
    console.log(">>> JS Customizado do Admin Carregado! <<<");

    // Seleciona todos os campos de senha
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(function(input) {
        // Evita duplicidade se o script rodar duas vezes
        if (input.parentNode.classList.contains('password-wrapper')) return;
        
        // 1. Configura o estilo do pai para posicionamento relativo
        const wrapper = document.createElement('div');
        wrapper.className = 'password-wrapper';
        wrapper.style.position = 'relative';
        wrapper.style.display = 'flex';
        wrapper.style.alignItems = 'center';
        wrapper.style.width = '100%';

        // 2. Insere o wrapper
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        // 3. Cria o botão do olho
        const toggleBtn = document.createElement('span');
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        
        // Estilo do botão para ficar flutuando à direita
        toggleBtn.style.position = 'absolute';
        toggleBtn.style.right = '10px';
        toggleBtn.style.cursor = 'pointer';
        toggleBtn.style.zIndex = '20';
        toggleBtn.style.padding = '5px';
        toggleBtn.style.color = '#6c757d';

        // 4. Ação de Clicar
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Impede submeter form sem querer
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // Troca ícone
            if (type === 'text') {
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                this.style.color = '#007bff'; // Fica azul quando visível
            } else {
                this.innerHTML = '<i class="fas fa-eye"></i>';
                this.style.color = '#6c757d';
            }
        });

        wrapper.appendChild(toggleBtn);
    });
});