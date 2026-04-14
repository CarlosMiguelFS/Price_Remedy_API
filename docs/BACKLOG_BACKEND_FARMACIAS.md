# Backlog de Back-end, Banco e Seguranca

## 1. Objetivo do Produto

Construir um back-end confiavel para consultar disponibilidade e preco de medicamentos por CEP, com:

- catalogo interno de medicamentos;
- tabela `de_para` entre medicamento interno e codigo de cada farmacia;
- registro historico das consultas;
- foco inicial total em back-end;
- front-end entrando depois no backlog.

O objetivo principal e tirar a regra de negocio de dentro dos arquivos Python hardcoded e centralizar isso no PostgreSQL.

---

## 2. O que o codigo faz hoje

### Fluxo atual

Hoje a API recebe:

- `cep`
- `produto` em texto livre

Depois ela chama cada integracao:

- `script_pharma/api.py`
- `script_pharma/drograsil.py`
- `script_pharma/pacheco.py`
- `script_pharma/indiana.py`
- `script_pharma/pague_menos.py`
- `script_pharma/drograria_sao_paulo.py`

Cada integracao possui o proprio `d_para` em memoria com o nome do medicamento e o codigo daquela farmacia.

### Problemas do modelo atual

1. O `de_para` esta espalhado em varios arquivos.
2. O nome do mesmo produto nao esta 100% padronizado entre farmacias.
3. O front precisaria acertar exatamente o mesmo texto esperado pelo Python.
4. Nao existe banco consolidando produtos, farmacias, consultas e historico.
5. Existe codigo antigo de banco em `base.py` usando MySQL e SQL por concatenacao de string, o que nao deve ser reaproveitado por seguranca.
6. A API ainda faz geocodificacao externa em `script_pharma/simple_geocoder.py`, o que hoje nao agrega para seu objetivo imediato de back-end.
7. Ha codigo de teste executando no import em alguns arquivos, por exemplo `pague_menos.py` e `santa_lucia.py`.

---

## 3. Decisao recomendada para o `de_para`

### Resposta curta

Sim: voce deve criar um ID interno seu.

Mas esse ID deve representar o **medicamento interno do sistema**, e nao o codigo da farmacia.

### Modelo mental correto

Voce tera:

- um `medicamento_id` interno, criado pelo seu banco;
- uma tabela de farmacias;
- uma tabela de relacionamento dizendo qual codigo cada farmacia usa para aquele medicamento.

Assim:

- seu sistema conhece o remedio por um ID proprio;
- cada farmacia continua com o codigo dela;
- o front nunca precisa saber SKU da farmacia.

### Exemplo

Medicamento interno:

- `medicamento_id = 101`
- `nome_exibicao = Mounjaro 2,5mg/ml`

Relacionamentos:

- Drogasil usa SKU `1272170`
- Pacheco usa SKU `887528`
- Indiana usa SKU `40221`

Logo, o front envia o medicamento interno do sistema, e o back-end converte isso para o codigo certo de cada farmacia.

---

## 4. Como a requisicao deve funcionar

### Melhor fluxo

1. A pessoa digita o nome do remedio no front.
2. O front chama um endpoint de busca de catalogo.
3. O back-end procura esse texto na tabela de aliases.
4. O back-end devolve as sugestoes com `medicamento_id`.
5. O usuario escolhe um item.
6. O front envia uma nova requisicao com:
   - `medicamento_id`
   - `cep`
7. O back-end busca no banco todos os codigos da farmacia para aquele `medicamento_id`.
8. O back-end consulta as farmacias e retorna os resultados.
9. O back-end grava a consulta no historico.

### Por que esse fluxo e melhor

- o front nao depende de texto exato;
- o nome digitado pode ter variacoes;
- voce evita erro por diferenca de escrita;
- o `de_para` fica no banco e nao hardcoded.

### Fluxo alternativo

Tambem da para o front enviar apenas texto e o back-end resolver tudo sozinho.

Exemplo:

- `GET /buscar?cep=29161716&termo=mounjaro 2,5`

O back-end:

- normaliza o texto;
- acha o alias correto;
- descobre o `medicamento_id`;
- segue com a busca.

Isso funciona, mas para o front o melhor futuro e ter autocomplete e enviar `medicamento_id`.

---

## 5. Modelagem recomendada no PostgreSQL

### 5.1 Tabela `farmacia`

Guarda as farmacias do sistema.

Campos sugeridos:

- `id` bigserial primary key
- `codigo_interno` varchar unique
- `nome` varchar
- `ativo` boolean default true
- `created_at` timestamptz
- `updated_at` timestamptz

Exemplo de `codigo_interno`:

- `drogasil`
- `pacheco`
- `indiana`
- `pague_menos`
- `drogaria_sao_paulo`

### 5.2 Tabela `medicamento`

Guarda o produto padrao do seu sistema.

Campos sugeridos:

- `id` bigserial primary key
- `slug` varchar unique
- `nome_exibicao` varchar
- `principio_ativo` varchar null
- `dosagem` varchar null
- `apresentacao` varchar null
- `ativo` boolean default true
- `created_at` timestamptz
- `updated_at` timestamptz

Exemplos:

- `mounjaro-2-5mg-0-5ml-4-canetas`
- `ritalina-10mg-30-comprimidos`

### 5.3 Tabela `medicamento_alias`

Guarda variacoes de busca.

Campos sugeridos:

- `id` bigserial primary key
- `medicamento_id` bigint references `medicamento(id)`
- `alias` varchar
- `alias_normalizado` varchar unique
- `created_at` timestamptz

Exemplos de alias:

- `mounjaro 2,5`
- `mounjaro 2.5`
- `mounjaro 2,5mg`
- `ritalina la 20`

### 5.4 Tabela `farmacia_medicamento`

Esta e a tabela principal do `de_para`.

Campos sugeridos:

- `id` bigserial primary key
- `farmacia_id` bigint references `farmacia(id)`
- `medicamento_id` bigint references `medicamento(id)`
- `codigo_farmacia` varchar
- `url_produto` text null
- `nome_farmacia_produto` varchar null
- `ativo` boolean default true
- `created_at` timestamptz
- `updated_at` timestamptz

Restricoes recomendadas:

- `unique (farmacia_id, medicamento_id)`
- `unique (farmacia_id, codigo_farmacia)`

### 5.5 Tabela `consulta_busca`

Guarda o historico de consultas.

Campos sugeridos:

- `id` bigserial primary key
- `medicamento_id` bigint null references `medicamento(id)`
- `termo_digitado` varchar
- `cep` varchar(8)
- `cep_prefixo` varchar(5)
- `quantidade_resultados` integer default 0
- `origem` varchar null
- `created_at` timestamptz

### 5.6 Tabela opcional `consulta_resultado`

Se quiser guardar snapshot do retorno de cada farmacia.

Campos sugeridos:

- `id` bigserial primary key
- `consulta_id` bigint references `consulta_busca(id)`
- `farmacia_id` bigint references `farmacia(id)`
- `codigo_farmacia` varchar
- `preco` numeric(10,2) null
- `preco_lista` numeric(10,2) null
- `estoque` integer null
- `endereco_resumido` varchar null
- `raw_payload` jsonb null
- `created_at` timestamptz

---

## 6. Recomendacao de privacidade e LGPD

### O que eu recomendo salvar

Para o seu objetivo atual, salve o minimo necessario:

- `medicamento_id`
- `termo_digitado`
- `cep`
- `cep_prefixo`
- data e hora
- quantidade de resultados

### O que eu recomendo NAO salvar agora

- nome da pessoa
- telefone
- email
- CPF
- endereco completo do usuario

Se seu objetivo e entender demanda por regiao, o `CEP` ja ajuda muito. Se quiser reduzir risco ainda mais, voce pode usar somente:

- `cep_prefixo` com os 5 primeiros digitos

Isso ja permite analise geografica sem guardar o CEP completo em todas as consultas.

### Ponto importante

Hoje, para descobrir lojas proximas, seu sistema envia o `CEP` para APIs externas das farmacias.

Entao existe uma verdade tecnica importante:

- se a busca depende de farmacias por CEP, o CEP do usuario necessariamente sera enviado para essas farmacias.

Se voce quer que nenhuma informacao do usuario saia para terceiros, entao esse modelo de consulta por CEP em tempo real nao atende 100% esse requisito.

O que voce pode fazer e:

- enviar somente o CEP, sem nome, email, telefone ou outros dados pessoais;
- nao usar mapas por enquanto;
- nao enviar dados do usuario para outros servicos alem das farmacias necessarias para a busca;
- remover geocodificacao externa enquanto ela nao for essencial.

---

## 7. Seguranca: banco na sua maquina Ubuntu

### Para homologacao

Sim, faz sentido usar sua maquina Ubuntu em casa para homologacao inicial, desde que:

- seja ambiente de teste;
- nao fique aberto para a internet toda;
- voce controle quem acessa;
- voce use usuario e senha fortes;
- voce nao exponha o PostgreSQL diretamente.

### Para producao

Nao e o mais seguro nem o mais estavel manter producao definitiva em um computador no quarto, principalmente se ele ficar exposto publicamente.

Riscos:

- queda de energia;
- internet residencial instavel;
- atualizacoes manuais;
- backup fraco;
- abertura indevida de portas;
- maquina pessoal misturada com ambiente de producao.

### Recomendacao pratica

Use assim:

- sua maquina Ubuntu = homologacao e testes internos
- servidor dedicado/VPS = producao depois

### Configuracoes minimas de seguranca no PostgreSQL

1. Criar usuario proprio da aplicacao, sem usar `postgres`.
2. Senha forte e unica.
3. Banco separado por ambiente:
   - `medradar_dev`
   - `medradar_hml`
   - `medradar_prod`
4. Nao expor a porta `5432` para qualquer IP.
5. Liberar acesso apenas para IPs controlados ou via VPN/SSH tunnel.
6. Configurar firewall no Ubuntu com `ufw`.
7. Revisar `postgresql.conf` e `pg_hba.conf`.
8. Fazer backup automatico.
9. Guardar credenciais em `.env`, nunca hardcoded.
10. Ativar logs e monitoramento basico.

### Configuracao recomendada de rede

O melhor para homologacao e um destes modelos:

- API e PostgreSQL na mesma maquina Ubuntu;
- API acessando PostgreSQL por rede privada/VPN;
- acesso administrativo por SSH, nunca por painel aberto para internet.

### O que evitar

- deixar PostgreSQL publico com `0.0.0.0/0`;
- usar senha fraca;
- usar usuario superadmin na aplicacao;
- salvar token e senha no codigo;
- reaproveitar o padrao de `base.py`.

---

## 8. Arquitetura recomendada do back-end

### Camadas sugeridas

1. `api`
   - recebe requisicao
   - valida entrada
   - retorna resposta

2. `services`
   - resolve produto
   - coordena consulta em farmacias
   - grava historico

3. `repositories`
   - fala com PostgreSQL
   - busca catalogo
   - busca `de_para`
   - grava consultas

4. `integrations`
   - um arquivo por farmacia
   - recebe `codigo_farmacia` e `cep`
   - retorna resposta padronizada

### Padrao ideal para as integracoes

As integracoes nao devem mais conhecer o nome do remedio.

Elas devem receber algo assim:

- `codigo_farmacia`
- `cep`
- `url_produto` opcional

Ou seja, o `d_para` sai dos arquivos Python e passa a vir do banco.

---

## 9. Exemplo de fluxo final da API

### Endpoint 1: buscar catalogo

`GET /medicamentos?termo=mounjaro 2,5`

Resposta:

```json
[
  {
    "id": 101,
    "nome_exibicao": "Mounjaro 2,5mg/ml",
    "slug": "mounjaro-2-5mg-ml"
  }
]
```

### Endpoint 2: consultar preco e disponibilidade

`POST /consultas`

```json
{
  "medicamento_id": 101,
  "cep": "29161716"
}
```

Resposta:

```json
{
  "consulta_id": 9001,
  "medicamento": "Mounjaro 2,5mg/ml",
  "resultados": [
    {
      "farmacia": "Drogasil",
      "codigo_farmacia": "1272170",
      "preco": 899.90,
      "estoque": 1
    }
  ]
}
```

---

## 10. SQL inicial sugerido

```sql
create table farmacia (
    id bigserial primary key,
    codigo_interno varchar(80) not null unique,
    nome varchar(150) not null,
    ativo boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table medicamento (
    id bigserial primary key,
    slug varchar(150) not null unique,
    nome_exibicao varchar(255) not null,
    principio_ativo varchar(255),
    dosagem varchar(120),
    apresentacao varchar(255),
    ativo boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table medicamento_alias (
    id bigserial primary key,
    medicamento_id bigint not null references medicamento(id),
    alias varchar(255) not null,
    alias_normalizado varchar(255) not null unique,
    created_at timestamptz not null default now()
);

create table farmacia_medicamento (
    id bigserial primary key,
    farmacia_id bigint not null references farmacia(id),
    medicamento_id bigint not null references medicamento(id),
    codigo_farmacia varchar(120) not null,
    url_produto text,
    nome_farmacia_produto varchar(255),
    ativo boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (farmacia_id, medicamento_id),
    unique (farmacia_id, codigo_farmacia)
);

create table consulta_busca (
    id bigserial primary key,
    medicamento_id bigint references medicamento(id),
    termo_digitado varchar(255),
    cep varchar(8) not null,
    cep_prefixo varchar(5),
    quantidade_resultados integer not null default 0,
    origem varchar(50),
    created_at timestamptz not null default now()
);

create table consulta_resultado (
    id bigserial primary key,
    consulta_id bigint not null references consulta_busca(id),
    farmacia_id bigint not null references farmacia(id),
    codigo_farmacia varchar(120),
    preco numeric(10,2),
    preco_lista numeric(10,2),
    estoque integer,
    endereco_resumido varchar(255),
    raw_payload jsonb,
    created_at timestamptz not null default now()
);
```

---

## 11. Backlog em formato PO

### Epic 1: Catalogo interno de medicamentos

**Objetivo:** permitir que o sistema tenha um identificador proprio para cada medicamento.

Historias:

- Como sistema, quero cadastrar medicamentos internos para nao depender de nomes hardcoded nos arquivos.
- Como sistema, quero cadastrar aliases de busca para entender variacoes digitadas pelo usuario.
- Como operador, quero ativar e desativar medicamentos sem alterar codigo-fonte.

### Epic 2: `de_para` por farmacia

**Objetivo:** relacionar cada medicamento interno ao codigo usado por cada farmacia.

Historias:

- Como sistema, quero relacionar `medicamento_id` com `codigo_farmacia` para montar consultas automaticas.
- Como operador, quero editar URL e codigo da farmacia sem publicar novo deploy.
- Como sistema, quero saber quais farmacias possuem cadastro valido para cada remedio.

### Epic 3: Historico e inteligencia de consultas

**Objetivo:** descobrir o que esta sendo mais buscado e onde.

Historias:

- Como negocio, quero registrar cada consulta para medir demanda por regiao.
- Como negocio, quero agrupar consultas por CEP ou prefixo de CEP.
- Como negocio, quero saber quais medicamentos tem mais procura.

### Epic 4: Seguranca e governanca

**Objetivo:** proteger dados e preparar ambiente seguro.

Historias:

- Como operador, quero rodar homologacao em ambiente controlado.
- Como sistema, quero armazenar apenas dados minimos necessarios do usuario.
- Como operador, quero credenciais fora do codigo e acesso restrito ao banco.

### Epic 5: Refatoracao do back-end

**Objetivo:** remover regras espalhadas e preparar a API para crescer.

Historias:

- Como sistema, quero buscar `de_para` no banco e nao no Python.
- Como sistema, quero registrar consulta e resultado em tabelas proprias.
- Como time, quero desativar o mapa por enquanto para reduzir complexidade.

---

## 12. To-do tecnico passo a passo

### Fase 1: Fundacao do banco

- [ ] Instalar PostgreSQL na maquina Ubuntu de homologacao.
- [ ] Criar banco de homologacao.
- [ ] Criar usuario da aplicacao com permissao minima.
- [ ] Configurar `.env` com host, porta, banco, usuario e senha.
- [ ] Criar as tabelas iniciais.
- [ ] Popular tabela `farmacia`.
- [ ] Popular tabela `medicamento`.
- [ ] Popular tabela `medicamento_alias`.
- [ ] Popular tabela `farmacia_medicamento` com os codigos atuais que hoje estao hardcoded.

### Fase 2: Seguranca minima obrigatoria

- [ ] Fechar acesso externo do PostgreSQL no firewall.
- [ ] Validar `pg_hba.conf` para aceitar apenas conexoes autorizadas.
- [ ] Nao usar usuario `postgres` na aplicacao.
- [ ] Tirar qualquer senha hardcoded do codigo.
- [ ] Criar rotina de backup.
- [ ] Definir logs basicos de aplicacao e banco.

### Fase 3: Refatoracao da aplicacao

- [ ] Criar camada de conexao com PostgreSQL.
- [ ] Criar repositório para `medicamento`, `alias`, `farmacia` e `farmacia_medicamento`.
- [ ] Criar servico para resolver `termo_digitado -> medicamento_id`.
- [ ] Ajustar integracoes para receber `codigo_farmacia` vindo do banco.
- [ ] Remover `d_para` hardcoded dos arquivos das farmacias.
- [ ] Criar endpoint de catalogo.
- [ ] Criar endpoint de consulta.
- [ ] Criar persistencia de `consulta_busca`.
- [ ] Criar persistencia opcional de `consulta_resultado`.

### Fase 4: Limpeza do escopo atual

- [ ] Remover o fluxo de mapa por enquanto.
- [ ] Desligar geocodificacao externa do fluxo principal.
- [ ] Remover prints de teste executados no import.
- [ ] Padronizar nomes de medicamentos que hoje estao divergentes entre integracoes.

### Fase 5: Homologacao

- [ ] Testar consulta de um medicamento com 1 farmacia.
- [ ] Testar consulta com todas as farmacias cadastradas.
- [ ] Validar insercao correta na tabela de consultas.
- [ ] Validar comportamento quando medicamento nao existe.
- [ ] Validar comportamento quando farmacia estiver fora do ar.
- [ ] Medir tempo medio de resposta.

### Fase 6: Preparacao para producao

- [ ] Subir codigo no servidor final.
- [ ] Subir PostgreSQL ou banco gerenciado em ambiente separado.
- [ ] Configurar HTTPS e proxy reverso.
- [ ] Revisar CORS.
- [ ] Revisar secrets e rotacao de senha.
- [ ] Habilitar monitoramento.

---

## 13. Ordem recomendada de execucao

1. Montar PostgreSQL em homologacao.
2. Criar modelagem do banco.
3. Inserir farmacias e medicamentos.
4. Migrar os `d_para` do Python para o banco.
5. Refatorar API para ler do banco.
6. Registrar consultas.
7. Tirar mapa e geocoding do fluxo principal.
8. Homologar tudo localmente.
9. So depois mover para servidor.

---

## 14. Decisoes que eu recomendo agora

### Decisao 1

Criar `medicamento_id` interno no seu banco.

### Decisao 2

O front nao deve mandar codigo de farmacia. Ele deve mandar:

- texto para busca, ou
- `medicamento_id` apos selecao

### Decisao 3

Salvar apenas o minimo necessario da consulta, principalmente:

- `medicamento_id`
- `termo_digitado`
- `cep`
- `cep_prefixo`
- data/hora

### Decisao 4

Homologar na sua maquina Ubuntu primeiro e producao depois em ambiente mais controlado.

### Decisao 5

Tirar mapa e geocoding agora para reduzir complexidade e risco.

---

## 15. Proximo passo mais inteligente

O melhor proximo passo tecnico e este:

1. criar o PostgreSQL;
2. criar essas tabelas;
3. migrar o `d_para` dos arquivos Python para o banco;
4. depois refatorar a API.

Se voce fizer isso nessa ordem, o restante do projeto fica muito mais simples de evoluir.
