# 🎓 Assistente Inteligente de Agendamento de Treinamentos

Sistema desenvolvido em Python com FastAPI para automatizar a criação de treinamentos corporativos e preparar convites para reuniões Microsoft Teams.

---

# Objetivo

Reduzir o trabalho manual na criação de treinamentos corporativos através de uma interface web simples, permitindo o cadastro de informações do treinamento e a geração automática de um payload estruturado para integração com Microsoft Teams e Microsoft Graph.

---

# Funcionalidades

- Cadastro de treinamentos

- Seleção de instrutores

- Inclusão de participantes por e-mail

-  Geração automática de descrição do treinamento

-  Cálculo automático do horário de início e término

-  Geração de payload JSON para criação de reuniões Teams

-  Download do payload gerado

-  API REST utilizando FastAPI

---

#  Arquitetura

```text
Interface Web
        ↓
FastAPI (Python)
        ↓
Geração de Payload JSON
        ↓
Microsoft Teams / Microsoft Graph
