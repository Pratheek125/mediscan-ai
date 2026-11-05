from gtts import gTTS
from pathlib import Path
LANGUAGES={"English":"en","Kannada":"kn","Hindi":"hi","Tamil":"ta","Telugu":"te","Malayalam":"ml"}
ROOT=Path(__file__).resolve().parents[1]

def generate_audio_for_language(text,language):
    out=ROOT/"outputs"/"audio"; out.mkdir(parents=True,exist_ok=True)
    path=out/f"{language}_Report.mp3"; gTTS(text=text,lang=LANGUAGES[language]).save(str(path)); return str(path)

def generate_audio():
    trans=ROOT/"outputs"/"translated_text"
    for language,code in LANGUAGES.items():
        p=trans/f"{language}.txt"
        if p.exists(): generate_audio_for_language(p.read_text(encoding="utf-8"),language)
