import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import msal
from dotenv import load_dotenv


load_dotenv()

TIMEZONE = "America/Fortaleza"
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def gerar_textos_treinamento(nome, data, horario, duracao, instrutor, publico):
    titulo = f"Treinamento {nome}"

    descricao = f"""
Olá!

Você está recebendo este convite para participar do treinamento: {nome}.

Objetivo do treinamento:
Capacitar os participantes no uso prático de {nome}, apresentando conceitos, funcionalidades principais e aplicações no ambiente corporativo.

Informações do treinamento:
- Tema: {nome}
- Data: {data}
- Horário: {horario}
- Duração: {duracao} minutos
- Instrutor: {instrutor}
- Público-alvo: {publico}

Conteúdo previsto:
- Apresentação da ferramenta
- Principais funcionalidades
- Exemplos práticos de uso
- Boas práticas
- Espaço para dúvidas

Atenciosamente,
Equipe de Educação Corporativa
""".strip()

    postagem_teams = f"""
    Novo treinamento disponível!

Tema: {nome}
Data: {data}
Horário: {horario}
Instrutor: {instrutor}

Este treinamento tem como objetivo apoiar os participantes no uso de {nome} dentro do ambiente corporativo, mostrando funcionalidades, boas práticas e exemplos práticos.

Contamos com sua participação!
""".strip()

    resumo_portal = f"""
Treinamento: {nome}

Este treinamento tem como objetivo desenvolver conhecimentos práticos sobre {nome}, com foco na aplicação da ferramenta em rotinas corporativas, melhoria da produtividade e colaboração entre equipes.
""".strip()

    return titulo, descricao, postagem_teams, resumo_portal


def converter_para_iso(data, horario, duracao):
    inicio_texto = f"{data} {horario}"
    inicio = datetime.strptime(inicio_texto, "%Y-%m-%d %H:%M")
    inicio = inicio.replace(tzinfo=ZoneInfo(TIMEZONE))

    fim = inicio + timedelta(minutes=int(duracao))

    return inicio.isoformat(), fim.isoformat()


def montar_payload_evento(titulo, descricao, inicio_iso, fim_iso, participantes):
    attendees = []

    for email in participantes:
        email = email.strip()

        if email:
            attendees.append(
                {
                    "emailAddress": {
                        "address": email
                    },
                    "type": "required"
                }
            )

    payload = {
        "subject": titulo,
        "body": {
            "contentType": "HTML",
            "content": descricao.replace("\n", "<br>")
        },
        "start": {
            "dateTime": inicio_iso,
            "timeZone": TIMEZONE
        },
        "end": {
            "dateTime": fim_iso,
            "timeZone": TIMEZONE
        },
        "attendees": attendees,
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness"
    }

    return payload


def obter_token_graph():
    client_id = os.getenv("GRAPH_CLIENT_ID")
    tenant_id = os.getenv("GRAPH_TENANT_ID", "common")

    if not client_id or client_id == "coloque_aqui_o_client_id":
        print("\nMicrosoft Graph não configurado.")
        print("O projeto vai gerar apenas o payload JSON.")
        return None

    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=authority
    )

    scopes = [
        "User.Read",
        "Calendars.ReadWrite"
    ]

    flow = app.initiate_device_flow(scopes=scopes)

    if "user_code" not in flow:
        print("Erro ao iniciar autenticação.")
        return None

    print("\nAutenticação Microsoft necessária:")
    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result["access_token"]

    print("Falha na autenticação.")
    print(result.get("error"))
    print(result.get("error_description"))

    return None


def criar_evento_graph(payload):
    token = obter_token_graph()

    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{GRAPH_BASE_URL}/me/events",
        headers=headers,
        json=payload
    )

    if response.status_code in [200, 201]:
        return response.json()

    print("\nErro ao criar evento no Microsoft Graph:")
    print(response.status_code)
    print(response.text)

    return None


def salvar_payload(payload):
    with open("convite_payload.json", "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=4)


def main():
    print("\n=== Assistente de Convites de Treinamento Teams ===\n")

    nome = input("Nome do treinamento: ")
    data = input("Data no formato AAAA-MM-DD: ")
    horario = input("Horário no formato HH:MM: ")
    duracao = input("Duração em minutos: ")
    instrutor = input("Instrutor: ")
    publico = input("Público-alvo: ")
    emails = input("E-mails dos participantes separados por vírgula: ")

    participantes = emails.split(",")

    titulo, descricao, postagem_teams, resumo_portal = gerar_textos_treinamento(
        nome=nome,
        data=data,
        horario=horario,
        duracao=duracao,
        instrutor=instrutor,
        publico=publico
    )

    inicio_iso, fim_iso = converter_para_iso(
        data=data,
        horario=horario,
        duracao=duracao
    )

    payload = montar_payload_evento(
        titulo=titulo,
        descricao=descricao,
        inicio_iso=inicio_iso,
        fim_iso=fim_iso,
        participantes=participantes
    )

    salvar_payload(payload)

    print("\n==============================")
    print("TÍTULO DO CONVITE")
    print("==============================")
    print(titulo)

    print("\n==============================")
    print("DESCRIÇÃO DO CONVITE TEAMS")
    print("==============================")
    print(descricao)

    print("\n==============================")
    print("POSTAGEM PARA TEAMS")
    print("==============================")
    print(postagem_teams)

    print("\n==============================")
    print("TEXTO PARA PORTAL")
    print("==============================")
    print(resumo_portal)

    print("\n==============================")
    print("PAYLOAD GERADO")
    print("==============================")
    print("Arquivo salvo como: convite_payload.json")

    resposta = input("\nDeseja tentar criar o convite no Microsoft Teams via Graph? s/n: ")

    if resposta.lower() == "s":
        evento = criar_evento_graph(payload)

        if evento:
            print("\nEvento criado com sucesso!")

            if "webLink" in evento:
                print("Link do evento:")
                print(evento["webLink"])

            if "onlineMeeting" in evento and evento["onlineMeeting"]:
                print("Link da reunião Teams:")
                print(evento["onlineMeeting"].get("joinUrl"))

        else:
            print("\nNão foi possível criar o evento agora.")
            print("Mas o payload foi salvo e o projeto está funcionando em modo demonstração.")
    else:
        print("\nModo demonstração concluído.")
        print("O arquivo convite_payload.json contém o modelo do convite.")


if __name__ == "__main__":
    main()