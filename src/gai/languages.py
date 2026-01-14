"""
Localization support for gai-cli.
"""

from typing import Dict

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "header_title": "GAI · Gemini CLI",
        "welcome": "Welcome to your new AI terminal assistant.",
        "api_key_check": "To get started, we need to set up your Google API key.",
        "api_key_missing": "API key cannot be empty.",
        "api_key_saved": "API key saved successfully!",
        "api_key_prompt": "Paste your API key here (hidden):",
        "get_key_link": "Get your API key here: https://ai.google.dev/",
        "thinking": "Thinking...",
        "goodbye": "Goodbye.",
        "agent_active": "Agent active... Scanning project.",
        "agent_scanning": "Scanning project files...",
        "agent_planning": "Agent is planning changes...",
        "applying_changes": "Applying changes...",
        "cancelled": "Cancelled.",
        "no_actions": "No actions proposed.",
        "plan_failed": "Failed to generate a plan.",
        "plan_title": "Plan:",
        "confirm_apply": "Apply these changes?",
        "verify_anyway": "No changes proposed. Run verification tests anyway?",
        "context_error": "Error loading context:",
        "gemini_error": "Gemini Error:",
        "unknown_command": "Unknown command.",
        "help_hint": "Type /help for commands",
        "help_title": "Available Commands:",
        "help_desc": """
        - `/help`:   Show commands
        - `/clear`:  Clear screen
        - `/theme`:  Change theme (default, dark, light)
        - `/lang`:   Change language (en, tr)
        - `/apikey`: Update API key
        - `/model`:  Show/Switch model
        - `/exit`:   Exit chat
        """,
        "model_current": "Current Model:",
        "model_available": "Available Models:",
        "model_switched": "Model switched to",
        "quota_exceeded": "API Quota/Rate Limit Exceeded. Try /model to switch models or wait a few minutes."
    },
    "tr": {
        "header_title": "GAI · Gemini Terminali",
        "welcome": "Yeni yapay zeka terminal asistanınıza hoş geldiniz.",
        "api_key_check": "Başlamak için Google API anahtarınızı ayarlamamız gerekiyor.",
        "api_key_missing": "API anahtarı boş olamaz.",
        "api_key_saved": "API anahtarı başarıyla kaydedildi!",
        "api_key_prompt": "API anahtarınızı buraya yapıştırın (gizli):",
        "get_key_link": "API anahtarınızı buradan alın: https://ai.google.dev/",
        "thinking": "Düşünüyor...",
        "goodbye": "Görüşürüz.",
        "agent_active": "Ajan aktif... Proje taranıyor.",
        "agent_scanning": "Proje dosyaları taranıyor...",
        "agent_planning": "Ajan değişiklikleri planlıyor...",
        "applying_changes": "Değişiklikler uygulanıyor...",
        "cancelled": "İptal edildi.",
        "no_actions": "Önerilen işlem yok.",
        "plan_failed": "Plan oluşturulamadı.",
        "plan_title": "Plan:",
        "confirm_apply": "Bu değişiklikler uygulansın mı?",
        "verify_anyway": "Değişiklik önerilmedi. Yine de doğrulama testleri çalıştırılsın mı?",
        "context_error": "Bağlam yükleme hatası:",
        "gemini_error": "Gemini Hatası:",
        "unknown_command": "Bilinmeyen komut.",
        "help_hint": "Komutlar için /help yazın",
        "help_title": "Kullanılabilir Komutlar:",
        "help_desc": """
        - `/help`:   Komutları göster
        - `/clear`:  Ekranı temizle
        - `/theme`:  Tema değiştir (default, dark, light)
        - `/lang`:   Dil değiştir (en, tr)
        - `/apikey`: API anahtarını güncelle
        - `/model`:  Modeli Göster/Değiştir
        - `/exit`:   Çıkış
        """,
        "model_current": "Aktif Model:",
        "model_available": "Kullanılabilir Modeller:",
        "model_switched": "Model değiştirildi:",
        "quota_exceeded": "API Kotası/Hız Limiti Aşıldı. /model komutu ile model değiştirebilir veya birkaç dakika bekleyebilirsiniz."
    }
}

def get_string(key: str, lang: str = "en") -> str:
    """Get a localized string."""
    lang_dict = STRINGS.get(lang, STRINGS["en"])
    return lang_dict.get(key, f"MISSING:{key}")
