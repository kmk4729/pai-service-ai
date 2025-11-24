from deep_translator import GoogleTranslator
import langdetect
from application.port.outbound.language_detection_port import LanguageDetectionPort

class LanguageDetectionAdapter(LanguageDetectionPort):

    def detect_language(self, text: str) -> str:
        try:
            return langdetect.detect(text)
        except:
            return "unknown"

    def translate_to_english(self, text: str) -> str:
        try:
            return GoogleTranslator(source='ko', target='en').translate(text)
        except Exception as e:
            print(f"Error during translation: {e}")
            return text
