"""
Jupiter AI Copilot - Translation Engine
Real-time translation with Google Translate API integration
"""

import sqlite3
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from language_manager import LanguageCode


@dataclass
class Translation:
    """Translation result"""
    source_language: LanguageCode
    target_language: LanguageCode
    source_text: str
    translated_text: str
    confidence: float = 1.0
    cached: bool = False


class TranslationEngine:
    """
    Translation engine with caching and terminology management
    Integrates with Google Translate API
    """
    
    # Security terminology that should remain consistent
    SECURITY_TERMS = {
        "CVE": "CVE",  # Always keep as-is
        "CVSS": "CVSS",
        "SQL Injection": {
            "es": "Inyección SQL",
            "fr": "Injection SQL",
            "de": "SQL-Injection",
            "ja": "SQLインジェクション",
            "zh-CN": "SQL注入",
            "ar": "حقن SQL",
            "pt": "Injeção SQL",
            "it": "SQL Injection",
            "ko": "SQL 인젝션"
        },
        "Cross-Site Scripting": {
            "es": "Cross-Site Scripting (XSS)",
            "fr": "Cross-Site Scripting (XSS)",
            "de": "Cross-Site Scripting (XSS)",
            "ja": "クロスサイトスクリプティング",
            "zh-CN": "跨站脚本攻击",
            "ar": "Cross-Site Scripting",
            "pt": "Cross-Site Scripting (XSS)",
            "it": "Cross-Site Scripting (XSS)",
            "ko": "크로스 사이트 스크립팅"
        },
        "Remote Code Execution": {
            "es": "Ejecución Remota de Código",
            "fr": "Exécution de Code à Distance",
            "de": "Remote Code Execution",
            "ja": "リモートコード実行",
            "zh-CN": "远程代码执行",
            "ar": "تنفيذ الكود عن بعد",
            "pt": "Execução Remota de Código",
            "it": "Esecuzione Remota di Codice",
            "ko": "원격 코드 실행"
        },
        "Buffer Overflow": {
            "es": "Desbordamiento de Búfer",
            "fr": "Dépassement de Tampon",
            "de": "Pufferüberlauf",
            "ja": "バッファオーバーフロー",
            "zh-CN": "缓冲区溢出",
            "ar": "تجاوز المخزن المؤقت",
            "pt": "Estouro de Buffer",
            "it": "Buffer Overflow",
            "ko": "버퍼 오버플로"
        },
        "Zero-Day": {
            "es": "Zero-Day",
            "fr": "Zero-Day",
            "de": "Zero-Day",
            "ja": "ゼロデイ",
            "zh-CN": "零日漏洞",
            "ar": "Zero-Day",
            "pt": "Zero-Day",
            "it": "Zero-Day",
            "ko": "제로데이"
        },
        "Authentication Bypass": {
            "es": "Omisión de Autenticación",
            "fr": "Contournement d'Authentification",
            "de": "Authentifizierungsumgehung",
            "ja": "認証バイパス",
            "zh-CN": "身份验证绕过",
            "ar": "تجاوز المصادقة",
            "pt": "Bypass de Autenticação",
            "it": "Bypass Autenticazione",
            "ko": "인증 우회"
        },
    }
    
    def __init__(self, db_path: str = "jupiter_i18n.db", api_key: Optional[str] = None):
        self.db_path = db_path
        self.api_key = api_key
        self.cache_ttl = timedelta(days=30)  # Cache translations for 30 days
        self._init_database()
    
    def _init_database(self):
        """Initialize translation database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Translation cache (already created by LanguageManager)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translation_cache (
                cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                source_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                context TEXT,
                cached_at TEXT,
                access_count INTEGER DEFAULT 0,
                expires_at TEXT
            )
        """)
        
        # Add index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_translation_lookup 
            ON translation_cache(source_language, target_language, source_text)
        """)
        
        # Custom terminology overrides
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS terminology (
                term_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_term TEXT NOT NULL,
                target_language TEXT NOT NULL,
                translated_term TEXT NOT NULL,
                category TEXT,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        self._init_terminology()
    
    def _init_terminology(self):
        """Initialize security terminology"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for term, translations in self.SECURITY_TERMS.items():
            if isinstance(translations, str):
                # Term stays the same in all languages
                continue
            
            for lang_code, translated in translations.items():
                cursor.execute("""
                    INSERT OR IGNORE INTO terminology 
                    (source_term, target_language, translated_term, category, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (term, lang_code, translated, "security", datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _get_cache_key(self, source_text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key"""
        content = f"{source_lang}:{target_lang}:{source_text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(
        self,
        source_text: str,
        source_lang: LanguageCode,
        target_lang: LanguageCode
    ) -> Optional[str]:
        """Get translation from cache"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT translated_text, expires_at, cache_id
            FROM translation_cache
            WHERE source_language = ?
              AND target_language = ?
              AND source_text = ?
        """, (source_lang.value, target_lang.value, source_text))
        
        row = cursor.fetchone()
        
        if row:
            translated_text, expires_at, cache_id = row
            
            # Check if expired
            if datetime.fromisoformat(expires_at) > datetime.now():
                # Update access count
                cursor.execute("""
                    UPDATE translation_cache 
                    SET access_count = access_count + 1
                    WHERE cache_id = ?
                """, (cache_id,))
                conn.commit()
                conn.close()
                return translated_text
        
        conn.close()
        return None
    
    def _save_to_cache(
        self,
        source_text: str,
        source_lang: LanguageCode,
        target_lang: LanguageCode,
        translated_text: str
    ):
        """Save translation to cache"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + self.cache_ttl
        
        cursor.execute("""
            INSERT INTO translation_cache 
            (source_language, target_language, source_text, translated_text, 
             cached_at, expires_at, access_count)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            source_lang.value,
            target_lang.value,
            source_text,
            translated_text,
            datetime.now().isoformat(),
            expires_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _apply_terminology(self, text: str, target_lang: LanguageCode) -> str:
        """Apply custom terminology to text"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_term, translated_term
            FROM terminology
            WHERE target_language = ?
        """, (target_lang.value,))
        
        replacements = dict(cursor.fetchall())
        conn.close()
        
        # Apply replacements (case-insensitive)
        result = text
        for source_term, translated_term in replacements.items():
            # Simple replacement (in production, would use more sophisticated matching)
            result = result.replace(source_term, translated_term)
        
        return result
    
    def translate(
        self,
        text: str,
        target_language: LanguageCode,
        source_language: Optional[LanguageCode] = None,
        context: str = ""
    ) -> Translation:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language (auto-detect if None)
            context: Context for better translation
        
        Returns:
            Translation object
        """
        
        # Auto-detect source language if not provided
        if not source_language:
            from language_manager import LanguageManager
            manager = LanguageManager()
            source_language = manager.detect_language(text)
        
        # Check if source and target are the same
        if source_language == target_language:
            return Translation(
                source_language=source_language,
                target_language=target_language,
                source_text=text,
                translated_text=text,
                confidence=1.0,
                cached=False
            )
        
        # Check cache first
        cached_translation = self._get_from_cache(text, source_language, target_language)
        
        if cached_translation:
            return Translation(
                source_language=source_language,
                target_language=target_language,
                source_text=text,
                translated_text=cached_translation,
                confidence=1.0,
                cached=True
            )
        
        # Perform translation (mock implementation)
        # In production, would call Google Translate API here
        translated_text = self._mock_translate(text, source_language, target_language)
        
        # Apply custom terminology
        translated_text = self._apply_terminology(translated_text, target_language)
        
        # Save to cache
        self._save_to_cache(text, source_language, target_language, translated_text)
        
        return Translation(
            source_language=source_language,
            target_language=target_language,
            source_text=text,
            translated_text=translated_text,
            confidence=0.95,
            cached=False
        )
    
    def _mock_translate(
        self,
        text: str,
        source_lang: LanguageCode,
        target_lang: LanguageCode
    ) -> str:
        """
        Mock translation (placeholder for Google Translate API)
        In production, would use actual Google Translate API
        """
        
        # Simple mock translations for demonstration
        mock_translations = {
            ("Critical vulnerability detected", LanguageCode.SPANISH): "Vulnerabilidad crítica detectada",
            ("Critical vulnerability detected", LanguageCode.FRENCH): "Vulnérabilité critique détectée",
            ("Critical vulnerability detected", LanguageCode.GERMAN): "Kritische Schwachstelle erkannt",
            ("Critical vulnerability detected", LanguageCode.JAPANESE): "重大な脆弱性が検出されました",
            ("Critical vulnerability detected", LanguageCode.CHINESE_SIMPLIFIED): "检测到严重漏洞",
            ("Critical vulnerability detected", LanguageCode.ARABIC): "تم اكتشاف ثغرة أمنية حرجة",
            ("Your system has 23 vulnerabilities", LanguageCode.SPANISH): "Su sistema tiene 23 vulnerabilidades",
            ("Your system has 23 vulnerabilities", LanguageCode.FRENCH): "Votre système a 23 vulnérabilités",
            ("Your system has 23 vulnerabilities", LanguageCode.GERMAN): "Ihr System hat 23 Schwachstellen",
            ("Your system has 23 vulnerabilities", LanguageCode.JAPANESE): "お客様のシステムには23個の脆弱性があります",
            ("Scan completed successfully", LanguageCode.SPANISH): "Escaneo completado exitosamente",
            ("Scan completed successfully", LanguageCode.FRENCH): "Analyse terminée avec succès",
            ("Scan completed successfully", LanguageCode.GERMAN): "Scan erfolgreich abgeschlossen",
        }
        
        key = (text, target_lang)
        if key in mock_translations:
            return mock_translations[key]
        
        # Fallback: return original with [TRANSLATED] prefix
        return f"[{target_lang.value}] {text}"
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: LanguageCode,
        source_language: Optional[LanguageCode] = None
    ) -> List[Translation]:
        """Translate multiple texts"""
        
        return [
            self.translate(text, target_language, source_language)
            for text in texts
        ]
    
    def clear_cache(self, older_than_days: Optional[int] = None):
        """Clear translation cache"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if older_than_days:
            cutoff = datetime.now() - timedelta(days=older_than_days)
            cursor.execute("""
                DELETE FROM translation_cache
                WHERE cached_at < ?
            """, (cutoff.isoformat(),))
        else:
            cursor.execute("DELETE FROM translation_cache")
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_statistics(self) -> Dict:
        """Get translation statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total cached translations
        cursor.execute("SELECT COUNT(*) FROM translation_cache")
        stats['total_cached'] = cursor.fetchone()[0]
        
        # Most translated languages
        cursor.execute("""
            SELECT target_language, COUNT(*) 
            FROM translation_cache 
            GROUP BY target_language 
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """)
        stats['top_target_languages'] = dict(cursor.fetchall())
        
        # Cache hit rate (translations with access_count > 1)
        cursor.execute("""
            SELECT COUNT(*) FROM translation_cache WHERE access_count > 1
        """)
        reused = cursor.fetchone()[0]
        stats['cache_hit_rate'] = reused / max(stats['total_cached'], 1)
        
        # Custom terms
        cursor.execute("SELECT COUNT(*) FROM terminology")
        stats['custom_terms'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    from language_manager import LanguageManager
    
    engine = TranslationEngine()
    manager = LanguageManager()
    
    print("Jupiter Translation Engine - Multi-Language Translation\n")
    
    # Test translations
    test_texts = [
        "Critical vulnerability detected",
        "Your system has 23 vulnerabilities",
        "Scan completed successfully"
    ]
    
    test_languages = [
        LanguageCode.SPANISH,
        LanguageCode.FRENCH,
        LanguageCode.GERMAN,
        LanguageCode.JAPANESE
    ]
    
    for text in test_texts:
        print(f"Original (EN): {text}")
        print()
        
        for lang in test_languages:
            translation = engine.translate(text, lang, LanguageCode.ENGLISH)
            cache_status = "✓ CACHED" if translation.cached else "✗ NEW"
            print(f"  {lang.value}: {translation.translated_text} {cache_status}")
        
        print("\n" + "-"*60 + "\n")
    
    # Test security terminology
    print("Security Terminology Translation:\n")
    
    security_text = "SQL Injection and Cross-Site Scripting are critical vulnerabilities"
    print(f"Original: {security_text}\n")
    
    for lang in [LanguageCode.SPANISH, LanguageCode.JAPANESE, LanguageCode.CHINESE_SIMPLIFIED]:
        translation = engine.translate(security_text, lang, LanguageCode.ENGLISH)
        print(f"{lang.value}: {translation.translated_text}")
    
    print("\n" + "="*60 + "\n")
    
    # Statistics
    stats = engine.get_statistics()
    print("Translation Statistics:")
    print(f"  Total Cached: {stats['total_cached']}")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
    print(f"  Custom Terms: {stats['custom_terms']}")
    print(f"  Top Target Languages: {stats['top_target_languages']}")
