# Controle de Gastos

Programa simples com interface gráfica pra anotar gastos do dia a dia e ver quanto foi gasto em cada categoria.

Feito pra Atividade Contínua 01 da disciplina Product: Analysis, Specification, Project & Implementation (ADS 5A).

## O que ele faz

- Adiciona um gasto com descrição, valor e categoria
- Mostra todos os gastos numa tabela com o total no rodapé
- Filtra a tabela por categoria (o total do rodapé acompanha o filtro)
- Remove um gasto selecionado na tabela (botão ou tecla Delete)
- Abre uma janela com o resumo por categoria (total e porcentagem)
- Limite de gastos do mês: barra que enche conforme gasta, fica vermelha e avisa quando passa do limite
- Salva tudo num arquivo `gastos.json`, então os dados continuam lá depois que fecha o programa

## Como rodar

Precisa só do Python 3 instalado. A interface usa o tkinter, que já vem junto com o Python, então não precisa instalar nenhuma biblioteca.

```
python gastos.py
```

## Estrutura

- `gastos.py` - todo o código do programa
- `gastos.json` - criado automaticamente na primeira vez que salva um gasto
- `config.json` - guarda o limite do mês
- `test_gastos.py` - testes da parte de cálculo (`python -m unittest test_gastos`)
