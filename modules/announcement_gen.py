"""
Kumbh-Drishti AI: Multilingual Public Announcement & Audio Broadcast Engine
Generates real-time crowd advisory scripts and audio announcements in Hindi, Marathi, and English.
"""

import os
import io
import wave
import struct
import math


class MultilingualAnnouncementEngine:
    def __init__(self):
        self.gtts_available = False
        try:
            from gtts import gTTS
            self.gtts = gTTS
            self.gtts_available = True
        except ImportError:
            self.gtts_available = False

    def generate_advisory_text(self, sector_name, risk_status, recommended_exit="Exit Gate 4"):
        """
        Generates contextual multilingual crowd advisory scripts.
        """
        if risk_status in ["CRITICAL", "HIGH RISK"]:
            hi_text = f"कृपया ध्यान दें! {sector_name} पर अत्यधिक भीड़ है और आगे जाना वर्जित है। कृपया तुरंत {recommended_exit} की ओर प्रस्थान करें और किसी भी प्रकार की धक्का-मुक्की न करें। प्रशासन के निर्देशों का पालन करें।"
            mr_text = f"कृपया लक्ष द्या! {sector_name} येथे प्रचंड गर्दी झाली असून पुढे जाणे सुरक्षित नाही. कृपया त्वरित {recommended_exit} च्या दिशेने मार्गक्रमण करा आणि शांतता राखा."
            en_text = f"Attention all devotees! High crowd density detected at {sector_name}. Movement towards the main bridge is restricted. Please proceed immediately towards {recommended_exit} in an orderly manner."
        elif risk_status == "MODERATE":
            hi_text = f"श्रद्धालुओं से अनुरोध है: {sector_name} पर भीड़ बढ़ रही है। कृपया कतार में चलें और अपने साथ आए बच्चों तथा बुजुर्गों का हाथ थामे रखें।"
            mr_text = f"भाविकांना नम्र विनंती: {sector_name} येथे गर्दी वाढत आहे. कृपया रांगेत चाला आणि लहान मुले व वृद्धांची काळजी घ्या."
            en_text = f"Public Announcement: Crowd inflow is steadily increasing at {sector_name}. Please move in queues and cooperate with the security personnel."
        else:
            hi_text = f"कुंभ मेला प्रशासन आपका स्वागत करता है। सभी घाटों पर स्थिति सामान्य व सुरक्षित है। स्वच्छता बनाए रखें।"
            mr_text = f"कुंभमेळा प्रशासन आपले स्वागत करत आहे. सर्व घाटांवर परिस्थिती सुरक्षित आहे. स्वच्छता राखा."
            en_text = f"Welcome to the Holy Kumbh. The crowd flow across all sectors is normal and safe. Have a peaceful darshan."

        return {
            "hindi": hi_text,
            "marathi": mr_text,
            "english": en_text
        }

    def generate_audio_bytes(self, text, lang='hi'):
        """
        Generates audio MP3 / WAV bytes for live playback in Streamlit.
        """
        if self.gtts_available:
            try:
                tts = self.gtts(text=text, lang=lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                return fp.read(), "audio/mp3"
            except Exception:
                pass
                
        # High-quality programmatic siren/beep fallback synthesizer if offline
        return self._generate_synthetic_beep_wav(), "audio/wav"

    def _generate_synthetic_beep_wav(self):
        """Generates a pleasant warning tone wave file in pure Python without dependencies."""
        sample_rate = 22050
        duration = 1.2
        num_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            frames = bytearray()
            for i in range(num_samples):
                t = float(i) / sample_rate
                # Frequency sweeps between 650Hz and 880Hz (police/announcement chime)
                freq = 650.0 + 230.0 * math.sin(2.0 * math.pi * 3.0 * t)
                val = int(16000.0 * math.sin(2.0 * math.pi * freq * t))
                frames.extend(struct.pack('<h', val))
                
            wav_file.writeframes(frames)
            
        buf.seek(0)
        return buf.read()
