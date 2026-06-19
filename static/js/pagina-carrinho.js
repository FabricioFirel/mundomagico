/* Página do carrinho: renderiza itens, calcula o orçamento e envia a reserva. */
(function () {
  "use strict";
  var lista = document.getElementById("lista-carrinho");
  var totalEl = document.getElementById("valor-total");
  var horasEl = document.getElementById("qtd-horas");
  var form = document.getElementById("form-reserva");
  var btn = document.getElementById("btn-finalizar");
  var dataEl = document.getElementById("data-evento");
  var qtdLocaisEl = document.getElementById("qtd-locais");
  var locaisEl = document.getElementById("locais");
  var dispEl = document.getElementById("disp-info");

  // Monta os campos de endereço conforme a quantidade de locais escolhida.
  function renderLocais() {
    var n = parseInt(qtdLocaisEl.value, 10) || 1;
    var atuais = locaisEl.querySelectorAll(".local-input");
    var valores = Array.prototype.map.call(atuais, function (i) { return i.value; });
    locaisEl.innerHTML = "";
    for (var k = 0; k < n; k++) {
      var lbl = document.createElement("label");
      lbl.textContent = "Local " + (k + 1);
      var inp = document.createElement("input");
      inp.type = "text"; inp.className = "local-input"; inp.required = true;
      inp.placeholder = "Bairro / endereço";
      if (valores[k]) inp.value = valores[k];
      lbl.appendChild(inp);
      locaisEl.appendChild(lbl);
    }
  }

  function coletarLocais() {
    return Array.prototype.map.call(
      locaisEl.querySelectorAll(".local-input"),
      function (i) { return i.value.trim(); }
    ).filter(Boolean);
  }

  // Consulta a disponibilidade do dia e ajusta as opções de locais.
  async function checarDisponibilidade() {
    if (!dataEl.value) { dispEl.hidden = true; btn.disabled = false; return; }
    try {
      var r = await fetch("/api/disponibilidade?data=" + encodeURIComponent(dataEl.value));
      var d = await r.json();
      Array.prototype.forEach.call(qtdLocaisEl.options, function (opt) {
        opt.disabled = Number(opt.value) > d.livres;
      });
      dispEl.hidden = false;
      if (d.livres <= 0) {
        dispEl.className = "disp-info cheio";
        dispEl.textContent = "Sem disponibilidade nesse dia. Por favor, escolha outra data.";
        btn.disabled = true;
      } else {
        dispEl.className = "disp-info ok";
        dispEl.textContent = d.livres + " de " + d.capacidade + " horário(s) livre(s) nesse dia.";
        btn.disabled = false;
        if (parseInt(qtdLocaisEl.value, 10) > d.livres) {
          qtdLocaisEl.value = String(d.livres);
          renderLocais();
        }
      }
    } catch (e) { dispEl.hidden = true; }
  }

  dataEl.addEventListener("change", checarDisponibilidade);
  qtdLocaisEl.addEventListener("change", renderLocais);

  var HORAS_BASE = 4;
  function moeda(v) { return "R$ " + (Number(v) || 0).toFixed(2).replace(".", ","); }
  function valorItem(i) { return Number(i.valor != null ? i.valor : i.preco) || 0; }

  function calcularTotal() {
    var itens = window.Carrinho.obter();
    var horas = parseInt(horasEl.value, 10);
    if (isNaN(horas) || horas < 1) horas = 1;
    // Valor base cobre até 4h; cada hora extra custa (base / 4) por item.
    var soma = itens.reduce(function (s, i) { return s + valorItem(i); }, 0);
    var extra = Math.max(0, horas - HORAS_BASE);
    var total = soma + extra * (soma / HORAS_BASE);
    totalEl.textContent = moeda(total);
    return total;
  }

  function render() {
    var itens = window.Carrinho.obter();
    if (!itens.length) {
      lista.innerHTML = '<p class="mensagem-vazio">Seu carrinho está vazio. <a href="/#inflaveis">Escolher brinquedos</a></p>';
      totalEl.textContent = moeda(0);
      return;
    }
    lista.innerHTML = itens.map(function (i, idx) {
      return '<div class="carrinho-item">' +
        '<img src="' + (i.imagem || "") + '" alt="" onerror="this.style.display=\'none\'" />' +
        '<div class="carrinho-item-info"><h4>' + escapeHtml(i.nome) + "</h4>" +
        '<p>' + moeda(valorItem(i)) + " até 4h</p></div>" +
        '<button class="btn-remover" data-remover="' + idx + '"><i class="fa-solid fa-trash"></i></button>' +
        "</div>";
    }).join("");
    calcularTotal();
  }

  function escapeHtml(v) {
    return String(v == null ? "" : v).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  lista.addEventListener("click", function (e) {
    var rem = e.target.closest("[data-remover]");
    if (!rem) return;
    window.Carrinho.remover(Number(rem.dataset.remover));
    render();
  });

  horasEl.addEventListener("input", calcularTotal);

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var itens = window.Carrinho.obter();
    if (!itens.length) { alert("Adicione algum brinquedo primeiro!"); return; }

    var locais = coletarLocais();
    if (!locais.length) { alert("Informe ao menos um local."); return; }

    var payload = {
      nome_cliente: document.getElementById("nome-cliente").value.trim(),
      telefone_cliente: document.getElementById("telefone-cliente").value.trim(),
      data_evento: dataEl.value,
      hora_inicio: document.getElementById("hora-inicio").value,
      qtd_horas: parseInt(horasEl.value, 10) || 1,
      locais: locais,
      itens: itens.map(function (i) { return { nome: i.nome, valor_ate_4h: valorItem(i) }; }),
    };

    btn.disabled = true;
    var textoOriginal = btn.innerHTML;
    btn.innerHTML = "Salvando pedido...";

    try {
      var resp = await fetch("/api/reservas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      var data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Erro ao salvar a reserva.");
      window.Carrinho.limpar();
      window.open(data.whatsapp_url, "_blank");
      lista.innerHTML = '<p class="mensagem-vazio">Pedido enviado! Continue a conversa no WhatsApp. 🎉</p>';
      totalEl.textContent = moeda(0);
    } catch (err) {
      alert(err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = textoOriginal;
    }
  });

  render();
})();
