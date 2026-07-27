from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json


app = FastAPI(
    title="Assistente de Convites de Treinamento",
    description="API com interface para gerar payloads de reuniões do Microsoft Teams.",
    version="1.0.0"
)

TIMEZONE_PYTHON = "America/Fortaleza"
TIMEZONE_POWER_AUTOMATE = "E. South America Standard Time"


class TreinamentoRequest(BaseModel):
    nome: str
    data: str
    horario: str
    duracao: int
    instrutor: str
    participantes: list[str]


def gerar_descricao(nome, data, horario, duracao, instrutor, participantes):
    descricao = f"""
Olá!

Você está recebendo este convite para participar do treinamento: {nome}.

Objetivo:
Capacitar os participantes no uso prático de {nome} no ambiente corporativo.

Informações:
- Data: {data}
- Horário: {horario}
- Duração: {duracao} minutos
- Instrutor: {instrutor}
- Participantes: {", ".join(participantes)}

Conteúdo previsto:
- Introdução à ferramenta
- Funcionalidades principais
- Exemplo prático
- Boas práticas
- Espaço para dúvidas

Atenciosamente,
Equipe de Educação Corporativa
""".strip()

    return descricao


def gerar_payload(dados: TreinamentoRequest):
    titulo = f"Treinamento {dados.nome}"

    descricao = gerar_descricao(
        nome=dados.nome,
        data=dados.data,
        horario=dados.horario,
        duracao=dados.duracao,
        instrutor=dados.instrutor,
        participantes=dados.participantes
    )

    inicio = datetime.strptime(
        f"{dados.data} {dados.horario}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=ZoneInfo(TIMEZONE_PYTHON))

    fim = inicio + timedelta(minutes=dados.duracao)

    payload = {
        "titulo": titulo,
        "descricao": descricao,
        "instrutor": dados.instrutor,
        "participantes": dados.participantes,
        "fuso_horario": TIMEZONE_POWER_AUTOMATE,
        "hora_inicio": inicio.strftime("%Y-%m-%dT%H:%M:%S"),
        "hora_fim": fim.strftime("%Y-%m-%dT%H:%M:%S"),
        "calendario": "Calendar"
    }

    return payload


@app.get("/")
def home():
    return {
        "mensagem": "API funcionando. Acesse /interface para gerar o payload da reunião."
    }

@app.get("/interface", response_class=HTMLResponse)
def interface():
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Gerador de Reuniões Teams</title>

<style>
body{
    font-family:Arial,sans-serif;
    background:#f4f6f8;
    padding:40px;
}

.container{
    max-width:750px;
    margin:auto;
    background:#fff;
    padding:30px;
    border-radius:12px;
    box-shadow:0 0 10px rgba(0,0,0,.1);
}

h1{
    color:#3b2e91;
}

label{
    display:block;
    margin-top:15px;
    font-weight:bold;
}

input,select,textarea{
    width:100%;
    padding:10px;
    margin-top:5px;
    border-radius:6px;
    border:1px solid #ccc;
    box-sizing:border-box;
}

button{
    margin-top:20px;
    padding:12px 20px;
    background:#6264a7;
    color:white;
    border:none;
    border-radius:6px;
    cursor:pointer;
}

button:hover{
    background:#4d4fa3;
}

pre{
    margin-top:20px;
    background:#1e1e1e;
    color:#dcdcdc;
    padding:15px;
    border-radius:8px;
    overflow:auto;
}
</style>

</head>
<body>

<div class="container">

<h1>Gerador de Reuniões Teams</h1>

<label>Nome do treinamento</label>
<input id="nome" value="Microsoft Planner">

<label>Data</label>
<input id="data" type="date" value="2026-08-10">

<label>Horário</label>
<input id="horario" type="time" value="14:00">

<label>Duração em minutos</label>
<input id="duracao" type="number" value="60">

<label>Instrutor</label>
<select id="instrutor">
    <option>Judyson Andrade Justino</option>
    <option>Laura Batista</option>
</select>

<label>E-mails dos participantes</label>

<textarea
id="participantes"
rows="6"
placeholder="judyson@empresa.com.br, laura@empresa.com.br"></textarea>

<button onclick="gerarPayload()">
Gerar payload da reunião
</button>

<pre id="resultado">O JSON aparecerá aqui...</pre>

<br><br>

<a href="/baixar-payload" target="_blank">
Baixar convite_payload.json
</a>

</div>

<script>

async function gerarPayload(){

    const dados={
        nome:document.getElementById("nome").value,
        data:document.getElementById("data").value,
        horario:document.getElementById("horario").value,
        duracao:parseInt(document.getElementById("duracao").value),
        instrutor:document.getElementById("instrutor").value,
        participantes:document
            .getElementById("participantes")
            .value
            .split(",")
            .map(e=>e.trim())
            .filter(e=>e)
    };

    const resposta=await fetch("/gerar-payload",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify(dados)
    });

    const json=await resposta.json();

    document.getElementById("resultado").textContent=
        JSON.stringify(json,null,4);

}

</script>

</body>
</html>
"""

@app.post("/gerar-payload")
def criar_payload(dados: TreinamentoRequest):
    payload = gerar_payload(dados)

    with open("convite_payload.json", "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=4)

    return {
        "mensagem": "Payload gerado com sucesso.",
        "payload": payload
    }


@app.get("/baixar-payload")
def baixar_payload():
    return FileResponse(
        path="convite_payload.json",
        filename="convite_payload.json",
        media_type="application/json"
    )