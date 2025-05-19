# app.py
from db import init_db, create_user, get_user_by_email, list_users, authenticate_user
import getpass

def prompt_create():
    print("\n=== Novo Usuário ===")
    name = input("Nome: ").strip()
    email = input("Email: ").strip()
    # senha sem eco
    password = input("Senha: ").strip()  
    #password = getpass.getpass("Senha: ") #nao da pra ver a senha
    try:
        user_id = create_user(name, email, password)
        print(f"✔ Usuário criado com ID {user_id}\n")
    except Exception as e:
        print("✖ Erro ao criar usuário:", e, "\n")

def prompt_view():
    print("\n=== Buscar Usuário por Email ===")
    email = input("Email: ").strip()
    user = get_user_by_email(email)
    if user:
        print("→", user, "\n")
    else:
        print("⚠ Usuário não encontrado.\n")

def prompt_list():
    print("\n=== Lista de Usuários ===")
    for u in list_users():
        print("→", u)
    print()

def prompt_login():
    print("\n=== Login ===")
    email = input("Email: ").strip()
    password = input("Senha: ").strip()
    user = authenticate_user(email, password)
    if user:
        uid, name, mail, created = user
        print(f"✔ Login bem-sucedido!  ID: {uid} | Nome: {name} | Email: {mail} | Cadastrado em: {created}\n")
    else:
        print("✖ Email ou senha incorretos.\n")

def main():
    init_db()
    menu = {
        '1': ("Criar usuário", prompt_create),
        '2': ("Buscar por email", prompt_view),
        '3': ("Listar todos",     prompt_list),
        '4': ("Login",            prompt_login),
        '0': ("Sair",             None)
    }
    while True:
        print("** MENU **")
        for k, (desc, _) in menu.items():
            print(f" {k} — {desc}")
        choice = input("Opção: ").strip()
        if choice == '0':
            print("Até logo!")
            break
        action = menu.get(choice)
        if action:
            action[1]()
        else:
            print("Opção inválida.\n")

if __name__ == "__main__":
    main()
