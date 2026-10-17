# LinkChains
### Protótipo de app P2P usando o Freechains


## Passo a Passo de Instalação e Execução

1. É preciso **instalar o Tkinter** e o **Custom Tkinter** para a interface gráfica:
    ```
    sudo apt install python3-tk
    pip3 install customtkinter --break-system-packages
    ```
2. É necessário **configurar o** caminho do **Freechains** para ele funcionar:
    ```
    eval $(luarocks --lua-version=5.4 path --bin) 
    freechains --version 
    ```
3. Após fazer o **download da pasta**, basta rodar:
    ```
    python3 linkchains.py
    ```

## O que **foi** implementado e ferramentas!
- UI simples para interação com a aplicação usando **CustomTkinter**
- Comunicação com o Freechains usando **Subprocess**
- Paralelização simples usando **Threading**
- 3 Tabelas SQL: Mensagens, Tags e Peers usando **SQLite3**


## O que **não** foi implementado!
- Descoberta mais intuitiva de novos peers
- Suporte a múltiplas cadeias
- Recomendações na busca