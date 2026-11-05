from deep_translator import GoogleTranslator
from pathlib import Path

LANGUAGES={"English":"en","Kannada":"kn","Hindi":"hi","Tamil":"ta","Telugu":"te","Malayalam":"ml"}
ROOT=Path(__file__).resolve().parents[1]

def translate_text(text):
    out={}
    d=ROOT/"outputs"/"translated_text"; d.mkdir(parents=True,exist_ok=True)
    for language,code in LANGUAGES.items():
        try: translated=text if code=="en" else GoogleTranslator(source="auto",target=code).translate(text)
        except Exception: translated=text+f"\n\n[Translation unavailable offline for {language}.]"
        out[language]=translated; (d/f"{language}.txt").write_text(translated,encoding="utf-8")
    return out

def translate_report(medical_report): return translate_text(medical_report)
