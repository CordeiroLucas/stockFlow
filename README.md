# 📦 StockFlow - Sistema de Controle de Estoque

Um sistema de gerenciamento de estoque escalável e moderno, desenvolvido com **Django**. O projeto foca em simplicidade, performance e experiência do usuário (UX), utilizando uma arquitetura Client-Server com validações robustas e interface responsiva (Mobile-First).

---

## 🚀 Funcionalidades

### 🔹 Gestão de Estoque
* **Dashboard Interativo:** Visão geral dos produtos com alertas visuais (texto vermelho) para itens com estoque baixo.
* **Entradas e Saídas:** Registro completo de movimentações com atualização automática do saldo.
* **Lógica de Saldo:** Cálculo dinâmico baseado no histórico de movimentações.

### 🔹 Regras de Negócio e Segurança
* **Limite Diário por CPF:** Bloqueio automático caso um CPF tente realizar mais de **3 retiradas** no mesmo dia (na modalidade padrão).
* **Validação Dupla de CPF:**
    * **Frontend:** Máscara automática de entrada e validação matemática em tempo real via JavaScript.
    * **Backend:** Validação de integridade no Python (`clean()`) para segurança dos dados.

### 🔹 Relatórios e Inteligência
* **Histórico Auditável:** Rastreabilidade completa de quem retirou, o que e quando.
* **Filtros Dinâmicos:** Busca por Nome do Produto, Tipo de Movimentação (Entrada/Saída) e Intervalo de Datas.
* **Exportação CSV Inteligente:** Botão que gera planilhas Excel baseadas **exatamente** nos filtros aplicados na tela (WYSIWYG).

### 🔹 UI/UX e Mobile
* **Tema Escuro/Claro (Dark Mode):** Sistema centralizado de temas com persistência (lembra a preferência do usuário) e troca fácil via Navbar.
* **Saída Rápida (Modo Mobile):**
    * Acesso rápido via ícone de **Tablet (📱)** na barra superior.
    * Interface simplificada com botões grandes e controle de quantidade (+/-).
    * Fluxo ágil sem exigência de CPF/Nome para operações internas rápidas.
* **Design Responsivo:** Construído com **Bootstrap 5.3**, adaptável a qualquer tamanho de tela.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3, Django 5.
* **Gerenciador de Pacotes:** uv.
* **Frontend:** HTML5, CSS3, JavaScript.
* **Framework Visual:** Bootstrap 5.3 (com suporte nativo a Dark Mode e ícones Bootstrap Icons).
* **Banco de Dados:** SQLite (Padrão inicial, pronto para escalar para PostgreSQL).

---

## 📂 Estrutura do Projeto

A organização segue o padrão MVT (Model-View-Template) do Django:

```text
stockFlow/
├── manage.py
├── stockFlow/       # Configurações do Projeto (settings, urls)
├── estoque/         # Aplicação Principal
│   ├── models.py    # Tabelas (Produto, Movimentacao) e Regras
│   ├── views.py     # Lógica (Dashboard, Filtros, CSV, Saída Rápida)
│   ├── forms.py     # Formulários e Validadores de CPF
│   ├── urls.py      # Rotas da aplicação
│   └── templates/   # Camada de Apresentação
│       └── estoque/
│           ├── base.html         # Template Mestre (Temas, Navbar)
│           ├── dashboard.html    # Tela Principal
│           ├── form_movimentacao.html # Form para registro de movimentações
│           ├── historico.html    # Relatórios e CSV
│           └── saida_rapida.html # Interface Mobile
```
⚡ Como Rodar o Projeto
Este projeto utiliza o uv para gerenciamento de dependências e ambientes virtuais pela sua alta performance.

1. Clonar e Configurar Ambiente
```Bash

# Clone o repositório
git clone <seu-link-do-git>

# Cria o ambiente virtual com uv já com as dependencias (cria a pasta .venv automaticamente)
uv sync

# Ativa o ambiente virtual (windows)
.venv/Scripts/activate

# Cria as migrações iniciais e tabelas no banco
python manage.py makemigrations
python manage.py migrate

# (Opcional) Crie um superusuário para acessar o painel administrativo
python manage.py createsuperuser
```

4. Executar
```Bash

python manage.py runserver
```
Acesse no navegador: http://127.0.0.1:8000

📖 Guia de Uso Rápido
Dashboard: Acompanhe o saldo. Use o botão "Nova Movimentação" para registros formais (exige CPF).

Saída Rápida (Ícone Tablet): Use no celular para retiradas ágeis. Basta selecionar o produto e a quantidade. Não contabiliza para o limite de CPF.

Histórico: Visualize todas as ações. Filtre por data ou produto e clique no botão Verde (CSV) para baixar o relatório exato daquela busca.

Temas: Clique no ícone de Lua/Sol na barra superior para alternar entre modo claro e escuro.

🔮 Roadmap (Futuro)
[ ] Implementação de Login de Usuário (@login_required).
