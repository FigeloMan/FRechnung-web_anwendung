"""
FRechnung ConfigManager (Cloud/Stateless Version)

Kein Keyring, keine Dateien, kein Serverzustand.
Firmendaten leben ausschliesslich im Browser (sessionStorage).
Diese Klasse ist nur fuer Kompatibilitaet mit pdf_generator.py.
"""

from typing import Dict, Any

DEFAULT_PROVIDER: Dict[str, str] = {
    "company_name": "", "owner": "", "contact_person": "",
    "phone": "", "email": "", "address": "", "tax_id": "",
    "tax_number": "", "creditor_reference": "", "bank": "",
    "bank_account": "", "bank_bic": "", "logo_path": "",
}


class ConfigManager:
    def get_service_provider(self) -> Dict[str, str]:
        return DEFAULT_PROVIDER.copy()

    def set_service_provider(self, data: Dict[str, str]) -> None:
        pass  # No-op

    def set_logo_path(self, path: str) -> None:
        pass  # No-op
