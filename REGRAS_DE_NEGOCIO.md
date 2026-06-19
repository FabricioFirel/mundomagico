# Regras de negócio — Mundo Mágico CM

## 1. Preço por brinquedo (valor até 4 horas)

- Cada brinquedo tem um **valor fixo que cobre o uso por até 4 horas**.
- **Não** é cobrado por hora dentro dessas 4 horas.

### Hora adicional

- Cada hora além das 4 horas custa **o valor base dividido por 4**.
- Fórmula do total de um item:
  - `total = valor_base + (horas - 4) × (valor_base / 4)`, quando `horas > 4`.
  - `total = valor_base`, quando `horas <= 4`.

**Exemplo (Tobogã Premium = R$ 380,00 até 4h):**

| Horas | Cálculo | Total |
|------:|---------|------:|
| 4h | R$ 380,00 | R$ 380,00 |
| 5h | 380 + 1 × 95 | R$ 475,00 |
| 6h | 380 + 2 × 95 | R$ 570,00 |

### Desconto

- Quando o cliente pega horas a mais, a empresa **costuma conceder um desconto**
  no valor final. Esse desconto é **definido manualmente no atendimento**, então
  o sistema apresenta o valor como **estimativa** e a negociação final acontece
  no WhatsApp.

## 2. Disponibilidade e múltiplos locais no mesmo dia

- A empresa atende **até 3 locais (eventos) no mesmo dia** (configurável em
  `MAX_EVENTOS_DIA`).
- O cliente pode reservar para **1, 2 ou 3 locais no mesmo dia**, conforme a
  necessidade — cada local ocupa um horário da capacidade do dia.
- Ao escolher a data, o site mostra **quantos horários ainda estão livres** e
  impede reservas acima da capacidade.
- O valor é calculado **por local** e multiplicado pela quantidade de locais.

## 3. Agenda do locador

- No painel administrativo há uma **Agenda** (calendário mensal) que mostra os
  eventos por dia, o status de cada um (pendente / pago / cancelado) e quantos
  horários ainda estão livres em cada data.

## 4. Status da reserva

- `pendente` → reserva criada, aguardando confirmação/pagamento.
- `pago` → reserva confirmada e paga (entra na receita).
- `cancelado` → reserva cancelada (libera o horário na agenda).
