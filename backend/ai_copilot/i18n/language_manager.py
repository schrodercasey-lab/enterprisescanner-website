"""
Jupiter AI Copilot - Language Manager
Multi-language support for global expansion
"""

import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum


class LanguageCode(Enum):
    """Supported language codes (ISO 639-1)"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    ARABIC = "ar"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    KOREAN = "ko"
    RUSSIAN = "ru"
    DUTCH = "nl"
    SWEDISH = "sv"
    POLISH = "pl"


class LocaleRegion(Enum):
    """Regional locale variations"""
    US = "US"              # United States
    GB = "GB"              # United Kingdom
    CA = "CA"              # Canada
    MX = "MX"              # Mexico
    ES = "ES"              # Spain
    FR = "FR"              # France
    DE = "DE"              # Germany
    JP = "JP"              # Japan
    CN = "CN"              # China
    TW = "TW"              # Taiwan
    KR = "KR"              # South Korea
    BR = "BR"              # Brazil
    IT = "IT"              # Italy
    SA = "SA"              # Saudi Arabia


@dataclass
class Language:
    """Language configuration"""
    code: LanguageCode
    name: str
    native_name: str
    direction: str = "ltr"  # ltr (left-to-right) or rtl (right-to-left)
    regions: List[LocaleRegion] = field(default_factory=list)
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    number_format: str = "1,234.56"
    currency_symbol: str = "$"


@dataclass
class UserLanguagePreference:
    """User language preferences"""
    user_id: str
    primary_language: LanguageCode
    fallback_language: LanguageCode = LanguageCode.ENGLISH
    region: Optional[LocaleRegion] = None
    timezone: str = "UTC"
    auto_detect: bool = True


class LanguageManager:
    """
    Main language management system
    Handles language detection, preferences, and localization
    """
    
    # Supported languages configuration
    LANGUAGES = {
        LanguageCode.ENGLISH: Language(
            code=LanguageCode.ENGLISH,
            name="English",
            native_name="English",
            direction="ltr",
            regions=[LocaleRegion.US, LocaleRegion.GB, LocaleRegion.CA],
            date_format="%m/%d/%Y",
            time_format="%I:%M %p",
            number_format="1,234.56",
            currency_symbol="$"
        ),
        LanguageCode.SPANISH: Language(
            code=LanguageCode.SPANISH,
            name="Spanish",
            native_name="Español",
            direction="ltr",
            regions=[LocaleRegion.ES, LocaleRegion.MX],
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format="1.234,56",
            currency_symbol="€"
        ),
        LanguageCode.FRENCH: Language(
            code=LanguageCode.FRENCH,
            name="French",
            native_name="Français",
            direction="ltr",
            regions=[LocaleRegion.FR, LocaleRegion.CA],
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format="1 234,56",
            currency_symbol="€"
        ),
        LanguageCode.GERMAN: Language(
            code=LanguageCode.GERMAN,
            name="German",
            native_name="Deutsch",
            direction="ltr",
            regions=[LocaleRegion.DE],
            date_format="%d.%m.%Y",
            time_format="%H:%M",
            number_format="1.234,56",
            currency_symbol="€"
        ),
        LanguageCode.JAPANESE: Language(
            code=LanguageCode.JAPANESE,
            name="Japanese",
            native_name="日本語",
            direction="ltr",
            regions=[LocaleRegion.JP],
            date_format="%Y年%m月%d日",
            time_format="%H:%M",
            number_format="1,234.56",
            currency_symbol="¥"
        ),
        LanguageCode.CHINESE_SIMPLIFIED: Language(
            code=LanguageCode.CHINESE_SIMPLIFIED,
            name="Chinese (Simplified)",
            native_name="简体中文",
            direction="ltr",
            regions=[LocaleRegion.CN],
            date_format="%Y年%m月%d日",
            time_format="%H:%M",
            number_format="1,234.56",
            currency_symbol="¥"
        ),
        LanguageCode.CHINESE_TRADITIONAL: Language(
            code=LanguageCode.CHINESE_TRADITIONAL,
            name="Chinese (Traditional)",
            native_name="繁體中文",
            direction="ltr",
            regions=[LocaleRegion.TW],
            date_format="%Y年%m月%d日",
            time_format="%H:%M",
            number_format="1,234.56",
            currency_symbol="NT$"
        ),
        LanguageCode.ARABIC: Language(
            code=LanguageCode.ARABIC,
            name="Arabic",
            native_name="العربية",
            direction="rtl",
            regions=[LocaleRegion.SA],
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format="1٬234٫56",
            currency_symbol="ر.س"
        ),
        LanguageCode.PORTUGUESE: Language(
            code=LanguageCode.PORTUGUESE,
            name="Portuguese",
            native_name="Português",
            direction="ltr",
            regions=[LocaleRegion.BR],
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format="1.234,56",
            currency_symbol="R$"
        ),
        LanguageCode.ITALIAN: Language(
            code=LanguageCode.ITALIAN,
            name="Italian",
            native_name="Italiano",
            direction="ltr",
            regions=[LocaleRegion.IT],
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format="1.234,56",
            currency_symbol="€"
        ),
        LanguageCode.KOREAN: Language(
            code=LanguageCode.KOREAN,
            name="Korean",
            native_name="한국어",
            direction="ltr",
            regions=[LocaleRegion.KR],
            date_format="%Y년 %m월 %d일",
            time_format="%H:%M",
            number_format="1,234.56",
            currency_symbol="₩"
        ),
    }
    
    def __init__(self, db_path: str = "jupiter_i18n.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize language management database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User language preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_language_preferences (
                user_id TEXT PRIMARY KEY,
                primary_language TEXT NOT NULL,
                fallback_language TEXT DEFAULT 'en',
                region TEXT,
                timezone TEXT DEFAULT 'UTC',
                auto_detect INTEGER DEFAULT 1,
                updated_at TEXT
            )
        """)
        
        # Translation cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translation_cache (
                cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                source_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                context TEXT,
                cached_at TEXT,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Localized UI strings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_strings (
                string_key TEXT NOT NULL,
                language_code TEXT NOT NULL,
                translated_value TEXT NOT NULL,
                category TEXT,
                updated_at TEXT,
                PRIMARY KEY (string_key, language_code)
            )
        """)
        
        # Language usage statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS language_usage (
                usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                language_code TEXT NOT NULL,
                feature TEXT,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        self._init_ui_strings()
    
    def _init_ui_strings(self):
        """Initialize common UI strings"""
        
        # Common UI elements
        ui_strings = {
            # Navigation
            "nav.dashboard": {
                "en": "Dashboard",
                "es": "Panel de Control",
                "fr": "Tableau de Bord",
                "de": "Übersicht",
                "ja": "ダッシュボード",
                "zh-CN": "仪表板",
                "ar": "لوحة القيادة",
                "pt": "Painel",
                "it": "Cruscotto",
                "ko": "대시보드"
            },
            "nav.vulnerabilities": {
                "en": "Vulnerabilities",
                "es": "Vulnerabilidades",
                "fr": "Vulnérabilités",
                "de": "Schwachstellen",
                "ja": "脆弱性",
                "zh-CN": "漏洞",
                "ar": "الثغرات الأمنية",
                "pt": "Vulnerabilidades",
                "it": "Vulnerabilità",
                "ko": "취약점"
            },
            "nav.scans": {
                "en": "Scans",
                "es": "Escaneos",
                "fr": "Analyses",
                "de": "Scans",
                "ja": "スキャン",
                "zh-CN": "扫描",
                "ar": "عمليات المسح",
                "pt": "Verificações",
                "it": "Scansioni",
                "ko": "스캔"
            },
            "nav.reports": {
                "en": "Reports",
                "es": "Informes",
                "fr": "Rapports",
                "de": "Berichte",
                "ja": "レポート",
                "zh-CN": "报告",
                "ar": "التقارير",
                "pt": "Relatórios",
                "it": "Report",
                "ko": "보고서"
            },
            # Actions
            "action.scan_now": {
                "en": "Scan Now",
                "es": "Escanear Ahora",
                "fr": "Analyser Maintenant",
                "de": "Jetzt Scannen",
                "ja": "今すぐスキャン",
                "zh-CN": "立即扫描",
                "ar": "مسح الآن",
                "pt": "Verificar Agora",
                "it": "Scansiona Ora",
                "ko": "지금 스캔"
            },
            "action.export": {
                "en": "Export",
                "es": "Exportar",
                "fr": "Exporter",
                "de": "Exportieren",
                "ja": "エクスポート",
                "zh-CN": "导出",
                "ar": "تصدير",
                "pt": "Exportar",
                "it": "Esporta",
                "ko": "내보내기"
            },
            "action.save": {
                "en": "Save",
                "es": "Guardar",
                "fr": "Enregistrer",
                "de": "Speichern",
                "ja": "保存",
                "zh-CN": "保存",
                "ar": "حفظ",
                "pt": "Salvar",
                "it": "Salva",
                "ko": "저장"
            },
            "action.cancel": {
                "en": "Cancel",
                "es": "Cancelar",
                "fr": "Annuler",
                "de": "Abbrechen",
                "ja": "キャンセル",
                "zh-CN": "取消",
                "ar": "إلغاء",
                "pt": "Cancelar",
                "it": "Annulla",
                "ko": "취소"
            },
            # Severity levels
            "severity.critical": {
                "en": "Critical",
                "es": "Crítico",
                "fr": "Critique",
                "de": "Kritisch",
                "ja": "重大",
                "zh-CN": "严重",
                "ar": "حرج",
                "pt": "Crítico",
                "it": "Critico",
                "ko": "치명적"
            },
            "severity.high": {
                "en": "High",
                "es": "Alto",
                "fr": "Élevé",
                "de": "Hoch",
                "ja": "高",
                "zh-CN": "高",
                "ar": "عالي",
                "pt": "Alto",
                "it": "Alto",
                "ko": "높음"
            },
            "severity.medium": {
                "en": "Medium",
                "es": "Medio",
                "fr": "Moyen",
                "de": "Mittel",
                "ja": "中",
                "zh-CN": "中",
                "ar": "متوسط",
                "pt": "Médio",
                "it": "Medio",
                "ko": "중간"
            },
            "severity.low": {
                "en": "Low",
                "es": "Bajo",
                "fr": "Faible",
                "de": "Niedrig",
                "ja": "低",
                "zh-CN": "低",
                "ar": "منخفض",
                "pt": "Baixo",
                "it": "Basso",
                "ko": "낮음"
            },
            # Status
            "status.scanning": {
                "en": "Scanning...",
                "es": "Escaneando...",
                "fr": "Analyse en cours...",
                "de": "Scannen...",
                "ja": "スキャン中...",
                "zh-CN": "扫描中...",
                "ar": "جاري المسح...",
                "pt": "Verificando...",
                "it": "Scansione...",
                "ko": "스캔 중..."
            },
            "status.complete": {
                "en": "Complete",
                "es": "Completo",
                "fr": "Terminé",
                "de": "Abgeschlossen",
                "ja": "完了",
                "zh-CN": "完成",
                "ar": "مكتمل",
                "pt": "Completo",
                "it": "Completato",
                "ko": "완료"
            },
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for key, translations in ui_strings.items():
            for lang_code, value in translations.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO ui_strings 
                    (string_key, language_code, translated_value, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (key, lang_code, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def detect_language(self, text: str) -> LanguageCode:
        """
        Detect language from text
        
        Args:
            text: Text to analyze
        
        Returns:
            Detected LanguageCode
        """
        
        # Simple character-based detection
        # In production, would use proper language detection library
        
        # Check for common character sets
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            # Chinese characters
            return LanguageCode.CHINESE_SIMPLIFIED
        
        if any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
            # Japanese hiragana/katakana
            return LanguageCode.JAPANESE
        
        if any('\uac00' <= char <= '\ud7af' for char in text):
            # Korean hangul
            return LanguageCode.KOREAN
        
        if any('\u0600' <= char <= '\u06ff' for char in text):
            # Arabic
            return LanguageCode.ARABIC
        
        # Default to English for Latin characters
        return LanguageCode.ENGLISH
    
    def set_user_preference(
        self,
        user_id: str,
        language: LanguageCode,
        region: Optional[LocaleRegion] = None,
        timezone: str = "UTC"
    ):
        """Set user language preference"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_language_preferences 
            (user_id, primary_language, region, timezone, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            language.value,
            region.value if region else None,
            timezone,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_preference(self, user_id: str) -> Optional[UserLanguagePreference]:
        """Get user language preference"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT primary_language, fallback_language, region, timezone, auto_detect
            FROM user_language_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserLanguagePreference(
                user_id=user_id,
                primary_language=LanguageCode(row[0]),
                fallback_language=LanguageCode(row[1]),
                region=LocaleRegion(row[2]) if row[2] else None,
                timezone=row[3],
                auto_detect=bool(row[4])
            )
        
        # Default to English
        return UserLanguagePreference(
            user_id=user_id,
            primary_language=LanguageCode.ENGLISH
        )
    
    def get_ui_string(
        self,
        key: str,
        language: LanguageCode,
        fallback: str = ""
    ) -> str:
        """
        Get localized UI string
        
        Args:
            key: String key (e.g., "nav.dashboard")
            language: Target language
            fallback: Fallback value if not found
        
        Returns:
            Localized string
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT translated_value 
            FROM ui_strings 
            WHERE string_key = ? AND language_code = ?
        """, (key, language.value))
        
        row = cursor.fetchone()
        
        if not row:
            # Try English fallback
            cursor.execute("""
                SELECT translated_value 
                FROM ui_strings 
                WHERE string_key = ? AND language_code = 'en'
            """, (key,))
            row = cursor.fetchone()
        
        conn.close()
        
        return row[0] if row else fallback
    
    def format_date(
        self,
        date: datetime,
        language: LanguageCode
    ) -> str:
        """Format date according to language conventions"""
        
        lang_config = self.LANGUAGES.get(language)
        if not lang_config:
            lang_config = self.LANGUAGES[LanguageCode.ENGLISH]
        
        return date.strftime(lang_config.date_format)
    
    def format_number(
        self,
        number: float,
        language: LanguageCode,
        decimals: int = 2
    ) -> str:
        """Format number according to language conventions"""
        
        lang_config = self.LANGUAGES.get(language)
        if not lang_config:
            lang_config = self.LANGUAGES[LanguageCode.ENGLISH]
        
        # Simple formatting based on language
        if language in [LanguageCode.GERMAN, LanguageCode.SPANISH, LanguageCode.ITALIAN, LanguageCode.PORTUGUESE]:
            # Use . for thousands, , for decimal
            formatted = f"{number:,.{decimals}f}"
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        elif language == LanguageCode.FRENCH:
            # Use space for thousands, , for decimal
            formatted = f"{number:,.{decimals}f}"
            formatted = formatted.replace(",", " ")
            formatted = formatted.replace(".", ",")
        else:
            # Use , for thousands, . for decimal (English, Japanese, Chinese, Korean)
            formatted = f"{number:,.{decimals}f}"
        
        return formatted
    
    def get_supported_languages(self) -> List[Language]:
        """Get list of supported languages"""
        return list(self.LANGUAGES.values())
    
    def log_usage(self, user_id: str, language: LanguageCode, feature: str = "general"):
        """Log language usage for analytics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO language_usage 
            (user_id, language_code, feature, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, language.value, feature, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """Get language usage statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total users by language
        cursor.execute("""
            SELECT primary_language, COUNT(*) 
            FROM user_language_preferences 
            GROUP BY primary_language
        """)
        stats['users_by_language'] = dict(cursor.fetchall())
        
        # Usage by language (last 30 days)
        cursor.execute("""
            SELECT language_code, COUNT(*) 
            FROM language_usage 
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY language_code 
            ORDER BY COUNT(*) DESC
        """)
        stats['usage_by_language'] = dict(cursor.fetchall())
        
        # Total UI strings
        cursor.execute("SELECT COUNT(DISTINCT string_key) FROM ui_strings")
        stats['total_ui_strings'] = cursor.fetchone()[0]
        
        # Translation cache size
        cursor.execute("SELECT COUNT(*) FROM translation_cache")
        stats['cached_translations'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    manager = LanguageManager()
    
    print("Jupiter Language Manager - Multi-Language Support\n")
    
    # Show supported languages
    print("Supported Languages:")
    for lang in manager.get_supported_languages():
        print(f"  {lang.native_name} ({lang.name}) - {lang.code.value}")
        print(f"    Direction: {lang.direction}, Date: {lang.date_format}")
    
    print("\n" + "="*60 + "\n")
    
    # Test user preferences
    user_id = "test_user_001"
    manager.set_user_preference(
        user_id,
        LanguageCode.JAPANESE,
        LocaleRegion.JP,
        "Asia/Tokyo"
    )
    
    pref = manager.get_user_preference(user_id)
    print(f"User Preference: {pref.primary_language.value} ({pref.region.value if pref.region else 'N/A'})")
    
    print("\n" + "="*60 + "\n")
    
    # Test UI string localization
    test_keys = ["nav.dashboard", "nav.vulnerabilities", "action.scan_now", "severity.critical"]
    test_languages = [
        LanguageCode.ENGLISH,
        LanguageCode.SPANISH,
        LanguageCode.JAPANESE,
        LanguageCode.ARABIC
    ]
    
    print("UI String Localization Examples:\n")
    for key in test_keys:
        print(f"Key: {key}")
        for lang in test_languages:
            value = manager.get_ui_string(key, lang)
            direction = manager.LANGUAGES[lang].direction
            print(f"  [{lang.value}] ({direction}): {value}")
        print()
    
    print("="*60 + "\n")
    
    # Test date/number formatting
    test_date = datetime(2025, 10, 17, 14, 30, 0)
    test_number = 1234567.89
    
    print("Date/Number Formatting:\n")
    for lang in [LanguageCode.ENGLISH, LanguageCode.GERMAN, LanguageCode.JAPANESE, LanguageCode.ARABIC]:
        formatted_date = manager.format_date(test_date, lang)
        formatted_number = manager.format_number(test_number, lang)
        print(f"{lang.value}: {formatted_date} | {formatted_number}")
    
    print("\n" + "="*60 + "\n")
    
    # Statistics
    stats = manager.get_statistics()
    print(f"Statistics:")
    print(f"  Total UI Strings: {stats['total_ui_strings']}")
    print(f"  Cached Translations: {stats['cached_translations']}")
    print(f"  Users by Language: {stats['users_by_language']}")
