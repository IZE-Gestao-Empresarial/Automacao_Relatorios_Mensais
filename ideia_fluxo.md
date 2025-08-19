## Fluxo de ideias para o n8n
Objetivo: o objetivo é escrever as ideias de como fazer o fluxo funcionar
Problema: preciso ter vários formulários para cada consultor com seus respectivos clientes, e esse formulário ficará sendo dinâmico, ou seja, mudará de acordo com o o consultores saindo da empresa ou não, os clientes saindo ou nao, ou até mesmo clientes mudando de consultor. E tudo isso precisa ser feito de forma automatizada pelo n8n.

### Ideia
- verificar se o consultor está na lista de consultores do banco de dados
- se não tiver, excluir o arquivo .py do github com o nome dele, ou adicionar um novo arquivo .py com as informações atualizadas do consultor
- 