# LinkChains
### Protótipo de app P2P usando o Freechains


## Passo a Passo de Instalação

1. É preciso **instalar o Tkinter**, o **Custom Tkinter** e o **Pillow** para a interface gráfica:
    ```
    sudo apt install python3-tk
    pip3 install customtkinter --break-system-packages
    pip3 install Pillow --break-system-packages
    ```
2. É necessário **instalar e configurar o** caminho do **Freechains** para ele funcionar:
    ```
    sudo apt install git openssh-client lua5.4 luarocks
    sudo luarocks --lua-version=5.4 install freechains
    eval $(luarocks --lua-version=5.4 path --bin) 
    freechains --version 
    ```
3. Após fazer o **download da pasta**, basta rodar:
    ```
    python3 linkchains.py
    ```

## Guia de Uso
Após executar ` python3 linkchains.py `, o programa deve abrir na janela de Setup.
Existem duas opções de Setup:
- Ser pioneiro e criar sua própria chain #torrents
- Clonar a de algum outro peer usando o seu IP Local na porta 8330 (`192.168.0.5:8330`, por exemplo)

OBS: Para descobrir o seu IP Local, rode ` hostname -I ` em outro terminal!!

Após o Setup, a janela principal do programa abre. Nela, temos alguns elementos:
- Coluna para fazer Posts (caixas de texto para Título, Tags e Link)
- 

## O que **foi** implementado e ferramentas!
- Lógica e programação em **Python** usando algumas bibliotecas.
- UI simples para interação do usuário com a aplicação usando **CustomTkinter**
- Comunicação com o Freechains usando **Subprocess**
- Paralelização simples usando **Threading**
- 3 Tabelas SQL: Mensagens, Tags e Peers usando **SQLite3**

**Em mais detalhes:**
- Criação de de um par chaves criptográficas para o usuário (ssh-keygen)
- Acesso a uma chain chamada "#torrents"
- Teste de pré-existência da chain ao abrir o programa (chain_existe)
- Instanciação local da chain (iniciar_chain)
    - Criação da chain como pioneiro (chain add)
    - Clonagem da chain a partir de um IP Local (clone)
- Banco de dados local para indexação de busca
- Teste de pré-existência e criação do DB (iniciar_db)
- Alocação de outra thread para sincronização periódica com o DB e com outros peers (worker_sync)
    - Recebimento da chain de peers conhecidos com timeout (recv_peers)
    - Sincronização periódica com o DB, verificando novos posts e ações na chain e os adicionando nas tabelas (salvar_post)
    - Remoção periódica do conteúdo revoked da chain no DB (limpar_revogados)
- Interface gráfica simples: botões como triggers para ações e formulários de texto para input (Setup e AppGUI)
- Botão de remoção de todos os dados para recomeçar o teste(remove_tudo): DB(deletar_db), chain (chains rem '#torrents') e chaves (rm -rf ./tmp/chaves)
- Adição de peers conhecidos via caixa de texto e salvamento no DB (add_peer_db)
- Exibição da reputação do usuário local (reps)
- Envio e formatação de posts em JSON (titulo, tags e link) para a chain (enviar_post)
    - Detecção de begs quando os reps do autor são 0
- Aba de begs, possibilita a aprovação com like de 500 reps (gui.py/aprovar_beg)
- Busca de posts via match de tags (busca)
- Uso da reputação nativa do freechains para posts: likes (gorjetas), dislikes (sinalização) e revokes (denuncia)
- Uso extensivo de try/except para erros

## O que **não** foi implementado!
- Suporte a múltiplas cadeias
- Identificação de peers por apelidos
- Remoção de peers conhecidos
- Quantidade de likes em cada post na busca
- Busca por pedaços de tags/títulos
- Recomendações na busca
- Visualização do próprio IP de forma visual/intuitiva dentro da aplicação