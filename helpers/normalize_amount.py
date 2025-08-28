# Normalizar monto a formato estándar 1,234.56
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
import re


def _normalize_amount_string(amount_input) -> str:
    s = str(amount_input).strip()
    if not s:
        return "0.00"
    # Quitar símbolos de moneda y espacios, dejar solo dígitos, punto, coma y guión
    s = re.sub(r'[^\d,\.\-]', '', s)
    negative = False
    if '-' in s:
        # Si empieza con -, considerar negativo
        if s.startswith('-'):
            negative = True
        s = s.replace('-', '')
    has_dot = '.' in s
    has_comma = ',' in s
    decimal_sep = None
    thousands_sep = None
    if has_dot and has_comma:
        # El separador decimal suele ser el último símbolo separador
        last_dot = s.rfind('.')
        last_comma = s.rfind(',')
        if last_dot > last_comma:
            decimal_sep = '.'
            thousands_sep = ','
        else:
            decimal_sep = ','
            thousands_sep = '.'
    elif has_dot:
        last_dot = s.rfind('.')
        digits_after = len(s) - last_dot - 1
        if digits_after in (1, 2):
            decimal_sep = '.'
        else:
            thousands_sep = '.'
    elif has_comma:
        last_comma = s.rfind(',')
        digits_after = len(s) - last_comma - 1
        if digits_after in (1, 2):
            decimal_sep = ','
        else:
            thousands_sep = ','
    # Eliminar miles
    s_clean = s.replace(thousands_sep, '') if thousands_sep else s
    # Unificar decimal a punto
    if decimal_sep and decimal_sep != '.':
        s_clean = s_clean.replace(decimal_sep, '.')
    # Si no hay decimales, agregar .00
    if '.' not in s_clean:
        s_clean = s_clean + '.00'
    try:
        value = Decimal(s_clean).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if negative:
            value = -value
    except (InvalidOperation, ValueError):
        return "0.00"
    return f"{value:,.2f}"