"""Compatibility adapter from legacy event calls to diagnostic logging."""

import re

import diagnosticLog


def _event_code(record_type, stage):
    raw_code = ".".join(part for part in (record_type, stage) if part)
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_code).strip("_.")
    return normalized[:100] or "legacy.event"


def writeCSV(
    tipo_registro,
    valor_venda_str,
    metodo_pag,
    etapa_erro,
    classe_erro,
    descricao_erro,
):
    """Keep existing call sites working while the CSV transport is retired."""
    code = _event_code(tipo_registro, etapa_erro)
    is_error = "erro" in tipo_registro.lower()
    level = "error" if is_error else "warning" if "alerta" in tipo_registro.lower() else "info"
    message = descricao_erro or tipo_registro
    context = {
        "valor_venda": valor_venda_str,
        "metodo_pagamento": metodo_pag,
        "classe_erro": classe_erro,
    }
    diagnosticLog.record_event(
        level,
        code,
        etapa_erro or "legacy",
        message,
        context=context,
        dedupe_key=code if is_error else None,
    )
