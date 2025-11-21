[![codecov](https://codecov.io/gh/HenriqueDSousa/todo-app/graph/badge.svg?token=9THOJE1DZH)](https://codecov.io/gh/HenriqueDSousa/todo-app)

# Todo App

## 1. Membros do Grupo

* Henrique Daniel de Sousa  
* João Luiz Figueiredo Cerqueira  
* Lucas Santana do Carmo Sacramento  
* Pedro Henrique Meireles de Almeida  

## 2. Sistema

O sistema desenvolvido é um **ToDo App** acessível via web.  
Ele permite que os usuários:

- ✅ Se registrem, se autentiquem e saiam de suas contas
- ✅ Criem novas tarefas com título, descrição e prioridade
- ✅ Definam deadlines para cada tarefa
- ✅ Marquem tarefas como concluídas
- ✅ Visualizem as tarefas pendentes e completas em uma lista organizada
- ✅ Criem tarefas para outros usuários
- ✅ Filtrem tarefas por status, prioridade e outros critérios
- ✅ Editem e excluam tarefas (com controle de permissões)

O objetivo principal é mostrar como **testes automatizados** auxiliam na manutenção e evolução de um sistema de software, garantindo confiabilidade e facilitando futuras alterações.

## 3. Ferramentas utilizadas

- **Backend e Frontend:** [Django](https://www.djangoproject.com/) — framework em Python para construção de aplicações web
- **Banco de Dados:** SQLite
- **Testes:** Pytest e Django Test Framework para garantir a qualidade do código e evitar regressões
- **Cobertura de Testes:** Coverage.py para mensurar a cobertura de código
- **CI/CD:** GitHub Actions para execução automática de testes em Linux, macOS e Windows
- **Publicação de Cobertura:** Codecov para publicação online dos relatórios de cobertura
- **Controle de versão:** [Git](https://git-scm.com/) com repositório no [GitHub](https://github.com/)
- **Gerenciamento de dependências:** `pip` e `venv` para o ambiente virtual Python
- **Qualidade de Código:** Flake8, Black e isort para formatação e linting

## 4. Como executar os testes localmente

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Configuração do ambiente

1. Clone o repositório:
```bash
git clone https://github.com/HenriqueDSousa/todo-app.git
cd todo-app
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```

4. Instale as dependências:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Executando os testes

1. Navegue para o diretório do projeto Django:
```bash
cd todoapp
```

2. Execute todos os testes com cobertura:
```bash
pytest --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
```

3. Para executar apenas os testes de unidade:
```bash
pytest -m unit
```

4. Para executar apenas os testes de integração:
```bash
pytest -m integration
```

5. Para executar testes de um arquivo específico:
```bash
pytest todos/tests.py
```

6. Para executar um teste específico:
```bash
pytest todos/tests.py::TaskModelTestCase::test_task_creation
```

### Visualizando o relatório de cobertura

Após executar os testes com cobertura, você pode visualizar o relatório HTML:
```bash
# O relatório HTML será gerado em htmlcov/index.html
# Abra este arquivo no navegador
```

### Executando o servidor de desenvolvimento

Para testar a aplicação manualmente:

1. Execute as migrações:
```bash
python manage.py migrate
```

2. Crie um superusuário (opcional):
```bash
python manage.py createsuperuser
```

3. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

4. Acesse a aplicação em: http://127.0.0.1:8000/

## 5. Estrutura de Testes

O projeto contém:

- **30+ testes de unidade** cobrindo modelos, formulários e visualizações
- **5 testes de integração** testando fluxos completos de usuário
- **Cobertura de código ≥ 80%** garantida através de testes abrangentes

### Testes de Unidade

Os testes de unidade estão organizados em:
- `TaskModelTestCase`: Testes do modelo Task (15 testes)
- `TaskFormTestCase`: Testes dos formulários (5 testes)
- `TaskViewTestCase`: Testes das visualizações (15 testes)
- `TaskFilterFormTestCase`: Testes do formulário de filtro (2 testes)

### Testes de Integração

Os testes de integração (`TaskIntegrationTestCase`) cobrem:
1. Fluxo completo de criação, edição, conclusão e exclusão de tarefas
2. Fluxo de atribuição de tarefas entre usuários
3. Fluxo de filtragem e paginação de tarefas
4. Fluxo de permissões entre diferentes usuários
5. Fluxo de gerenciamento de deadlines e tarefas vencidas

## 6. CI/CD

O projeto utiliza GitHub Actions para execução automática de testes em cada commit e pull request. O pipeline:

- Executa testes em **Linux, macOS e Windows**
- Testa em múltiplas versões do Python (3.11 e 3.12)
- Executa verificações de qualidade de código (flake8, black, isort)
- Publica relatórios de cobertura no Codecov

O workflow está configurado em `.github/workflows/ci.yml`.

## 7. Cobertura de Testes

A cobertura de testes é monitorada através do Codecov. O badge no topo deste README mostra a cobertura atual do projeto.

Para visualizar o relatório completo de cobertura, acesse: [Codecov Dashboard](https://codecov.io/gh/HenriqueDSousa/todo-app)

## 8. Estrutura do Projeto

```
todo-app/
├── .github/
│   └── workflows/
│       └── ci.yml              # Configuração do GitHub Actions
├── todoapp/
│   ├── accounts/              # App de autenticação
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── todos/                 # App principal de tarefas
│   │   ├── models.py          # Modelo Task
│   │   ├── views.py           # Visualizações CRUD
│   │   ├── forms.py           # Formulários
│   │   ├── urls.py            # Rotas
│   │   ├── admin.py           # Interface administrativa
│   │   └── tests.py            # Testes completos
│   ├── templates/             # Templates HTML
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── accounts/
│   │   └── todos/
│   ├── todoapp/
│   │   ├── settings.py
│   │   └── urls.py
│   └── manage.py
├── requirements.txt           # Dependências de produção
├── requirements-dev.txt       # Dependências de desenvolvimento
├── pytest.ini                # Configuração do pytest
├── .coveragerc               # Configuração do coverage
└── README.md                 # Este arquivo
```

## 9. Funcionalidades Implementadas

### Autenticação
- Registro de novos usuários
- Login e logout
- Perfis de usuário estendidos

### Gerenciamento de Tarefas
- Criação de tarefas com título, descrição, deadline e prioridade
- Visualização de lista de tarefas com paginação
- Detalhes de tarefas individuais
- Edição de tarefas (com controle de permissões)
- Exclusão de tarefas (apenas pelo criador)
- Marcação de tarefas como concluídas/pendentes
- Atribuição de tarefas para outros usuários

### Filtros e Busca
- Filtro por status (pendente, em progresso, concluída)
- Filtro por prioridade (baixa, média, alta)
- Opção para ocultar tarefas concluídas
- Filtro para mostrar apenas tarefas atribuídas ao usuário atual
- Indicador de tarefas vencidas

### Segurança e Permissões
- Apenas usuários autenticados podem criar tarefas
- Usuários podem visualizar apenas suas próprias tarefas ou tarefas atribuídas a eles
- Apenas o criador ou o usuário atribuído podem editar uma tarefa
- Apenas o criador pode excluir uma tarefa

## 10. Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

Certifique-se de que todos os testes passem e que a cobertura de código permaneça acima de 80%.

## 11. Licença

Este projeto foi desenvolvido para fins educacionais como parte de um trabalho prático de Teste de Software.  