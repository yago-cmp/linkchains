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
- Coluna para fazer Posts (Título, Tags e Link)
- 

## O que **foi** implementado e ferramentas!
- UI simples para interação com a aplicação usando **CustomTkinter**
- Comunicação com o Freechains usando **Subprocess**
- Paralelização simples usando **Threading**
- 3 Tabelas SQL: Mensagens, Tags e Peers usando **SQLite3**


## O que **não** foi implementado!
- Descoberta mais intuitiva de novos peers
- Suporte a múltiplas cadeias
- Recomendações na busca