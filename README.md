
# Sistema de Filas

Esse projeto busca otimizar a transparência e o tempo que os cidadãos brasileiros passam na fila do SUS.




## Variáveis de Ambiente

Para rodar esse projeto, você vai precisar adicionar as seguintes variáveis de ambiente no seu .env

`SECRET_KEY` = "Exemplo123"


## Rodando o programa

Para poder rodar o programa você deve primeiramente baixar as dependências necessarias atraves do comando:

```bash
  pip install -r requirements.txt
```
Em seguida você deve realizar os seguintes comandos para criar as tables do banco de dados

```bash
  python3 manage.py makemigrations
```

```bash
  python3 manage.py migrate
```
Por fim rodando o seguinte comando você iniciara o servidor de desenvolvimento

```bash
  python3 manage.py runserver
```
## Autores

- [@Gs-G2](https://github.com/Gs-G2)
- [@Gustavo-CS](https://github.com/Gustavo-CS)
- [@juancarlosribeiro](https://github.com/juancarlosribeiro)
- [@LuiFyt](https://github.com/LuiFyt)
- [@marianunx](https://github.com/marianunx)

