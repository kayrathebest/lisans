#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Userbot with CustomTkinter GUI
No Console Input - Full GUI Control
"""

import os
os.environ["PYROGRAM_NO_CRYPTO"] = "1"

import customtkinter as ctk
import asyncio
import random
import requests
import threading
from pyrogram import Client, errors
from pyrogram.errors import FloodWait, PhoneNumberInvalid, PhoneCodeInvalid, SessionPasswordNeeded
from typing import Optional, Set
import json


# ==================== CONFIG ====================
LISANS_URL = "https://raw.githubusercontent.com/kayrathebest/lisans/refs/heads/main/lisanslar"
SESSION_FILE = "userbot_session"
GONDERILENLER_FILE = "gonderilenler.txt"

# Renkler
SIYAH = "#000000"
ALTIN_SARISI = "#FFD700"

# API Credentials (Kullanıcı doldurmalı)
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"


# ==================== LISANS SİSTEMİ ====================
def lisans_dogrula(key: str) -> bool:
    """GitHub'dan lisans listesini çeker ve doğrular"""
    try:
        response = requests.get(LISANS_URL, timeout=10)
        response.raise_for_status()

        lisanslar = response.text.strip().split('\n')
        lisanslar = [l.strip() for l in lisanslar if l.strip()]

        return key.strip() in lisanslar
    except Exception as e:
        print(f"Lisans doğrulama hatası: {e}")
        return False


# ==================== HAFIZA SİSTEMİ ====================
class HafizaSistemi:
    """Gönderilen kullanıcıları takip eder"""

    def __init__(self, dosya_yolu: str):
        self.dosya_yolu = dosya_yolu
        self.gonderilenler: Set[int] = self._yukle()

    def _yukle(self) -> Set[int]:
        """Dosyadan gönderilen kullanıcıları yükle"""
        if not os.path.exists(self.dosya_yolu):
            return set()

        try:
            with open(self.dosya_yolu, 'r', encoding='utf-8') as f:
                return set(int(line.strip()) for line in f if line.strip().isdigit())
        except Exception:
            return set()

    def kaydet(self, user_id: int):
        """Kullanıcı ID'sini kaydet"""
        self.gonderilenler.add(user_id)
        try:
            with open(self.dosya_yolu, 'a', encoding='utf-8') as f:
                f.write(f"{user_id}\n")
        except Exception as e:
            print(f"Kaydetme hatası: {e}")

    def kontrol(self, user_id: int) -> bool:
        """Kullanıcıya daha önce mesaj gönderildi mi?"""
        return user_id in self.gonderilenler

    def sifirla(self):
        """Hafızayı temizle"""
        self.gonderilenler.clear()
        if os.path.exists(self.dosya_yolu):
            os.remove(self.dosya_yolu)


# ==================== LISANS EKRANI ====================
class LisansEkrani(ctk.CTk):
    """İlk açılışta lisans key kontrolü yapan ekran"""

    def __init__(self):
        super().__init__()

        self.title("Telegram Userbot - Lisans Doğrulama")
        self.geometry("500x300")
        self.resizable(False, False)

        # Renk teması
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=SIYAH)

        self.lisans_gecerli = False

        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Lisans ekranı arayüzünü oluştur"""
        # Başlık
        baslik = ctk.CTkLabel(
            self,
            text="🔐 LİSANS DOĞRULAMA",
            font=("Arial", 24, "bold"),
            text_color=ALTIN_SARISI
        )
        baslik.pack(pady=40)

        # Açıklama
        aciklama = ctk.CTkLabel(
            self,
            text="Lisans anahtarınızı girin:",
            font=("Arial", 14),
            text_color=ALTIN_SARISI
        )
        aciklama.pack(pady=10)

        # Lisans girişi
        self.lisans_entry = ctk.CTkEntry(
            self,
            width=350,
            height=40,
            font=("Arial", 14),
            fg_color=SIYAH,
            border_color=ALTIN_SARISI,
            text_color=ALTIN_SARISI,
            placeholder_text="Lisans Key"
        )
        self.lisans_entry.pack(pady=15)

        # Doğrula butonu
        self.dogrula_btn = ctk.CTkButton(
            self,
            text="Doğrula",
            width=200,
            height=40,
            font=("Arial", 16, "bold"),
            fg_color=ALTIN_SARISI,
            text_color=SIYAH,
            hover_color="#DAA520",
            command=self._lisans_dogrula
        )
        self.dogrula_btn.pack(pady=20)

        # Durum mesajı
        self.durum_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12),
            text_color="#FF0000"
        )
        self.durum_label.pack(pady=10)

    def _lisans_dogrula(self):
        """Lisans anahtarını doğrula"""
        key = self.lisans_entry.get().strip()

        if not key:
            self.durum_label.configure(text="⚠️ Lütfen lisans anahtarı girin!", text_color="#FF0000")
            return

        self.dogrula_btn.configure(state="disabled", text="Doğrulanıyor...")
        self.durum_label.configure(text="🔄 Kontrol ediliyor...", text_color=ALTIN_SARISI)

        # Thread'de doğrulama yap
        threading.Thread(target=self._dogrulama_thread, args=(key,), daemon=True).start()

    def _dogrulama_thread(self, key: str):
        """Arka planda lisans doğrulama"""
        gecerli = lisans_dogrula(key)

        self.after(100, lambda: self._dogrulama_sonuc(gecerli))

    def _dogrulama_sonuc(self, gecerli: bool):
        """Doğrulama sonucunu işle"""
        if gecerli:
            self.durum_label.configure(text="✅ Lisans geçerli! Yönlendiriliyorsunuz...", text_color="#00FF00")
            self.lisans_gecerli = True
            self.after(1000, self.destroy)
        else:
            self.durum_label.configure(text="❌ Geçersiz lisans anahtarı!", text_color="#FF0000")
            self.dogrula_btn.configure(state="normal", text="Doğrula")


# ==================== ANA UYGULAMA ====================
class TelegramUserbotGUI(ctk.CTk):
    """Ana Userbot arayüzü"""

    def __init__(self):
        super().__init__()

        self.title("Telegram Userbot - GUI Control")
        self.geometry("600x700")
        self.resizable(False, False)

        self.configure(fg_color=SIYAH)

        # Pyrogram client
        self.client: Optional[Client] = None
        self.hafiza = HafizaSistemi(GONDERILENLER_FILE)
        self.calisma_durumu = False

        # Auth state
        self.phone_code_hash: Optional[str] = None

        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Ana arayüzü oluştur"""
        # Başlık
        baslik = ctk.CTkLabel(
            self,
            text="📱 TELEGRAM USERBOT",
            font=("Arial", 26, "bold"),
            text_color=ALTIN_SARISI
        )
        baslik.pack(pady=20)

        # API Bilgileri Frame
        api_frame = ctk.CTkFrame(self, fg_color=SIYAH, border_color=ALTIN_SARISI, border_width=2)
        api_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(api_frame, text="API ID:", font=("Arial", 12), text_color=ALTIN_SARISI).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.api_id_entry = ctk.CTkEntry(api_frame, width=200, fg_color=SIYAH, border_color=ALTIN_SARISI, text_color=ALTIN_SARISI)
        self.api_id_entry.grid(row=0, column=1, padx=10, pady=5)
        self.api_id_entry.insert(0, API_ID)

        ctk.CTkLabel(api_frame, text="API Hash:", font=("Arial", 12), text_color=ALTIN_SARISI).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.api_hash_entry = ctk.CTkEntry(api_frame, width=200, fg_color=SIYAH, border_color=ALTIN_SARISI, text_color=ALTIN_SARISI)
        self.api_hash_entry.grid(row=1, column=1, padx=10, pady=5)
        self.api_hash_entry.insert(0, API_HASH)

        # Telefon Numarası
        ctk.CTkLabel(self, text="Telefon Numarası (+90...):", font=("Arial", 12), text_color=ALTIN_SARISI).pack(pady=(15, 5))
        self.telefon_entry = ctk.CTkEntry(
            self,
            width=400,
            height=35,
            fg_color=SIYAH,
            border_color=ALTIN_SARISI,
            text_color=ALTIN_SARISI,
            placeholder_text="+905551234567"
        )
        self.telefon_entry.pack(pady=5)

        # Giriş Yap Butonu
        self.giris_btn = ctk.CTkButton(
            self,
            text="🔑 Giriş Yap (Kod Gönder)",
            width=250,
            height=35,
            font=("Arial", 14, "bold"),
            fg_color=ALTIN_SARISI,
            text_color=SIYAH,
            hover_color="#DAA520",
            command=self._giris_yap
        )
        self.giris_btn.pack(pady=10)

        # Onay Kodu
        ctk.CTkLabel(self, text="Onay Kodu:", font=("Arial", 12), text_color=ALTIN_SARISI).pack(pady=(15, 5))
        self.kod_entry = ctk.CTkEntry(
            self,
            width=400,
            height=35,
            fg_color=SIYAH,
            border_color=ALTIN_SARISI,
            text_color=ALTIN_SARISI,
            placeholder_text="12345"
        )
        self.kod_entry.pack(pady=5)

        # Kodu Onayla Butonu
        self.onayla_btn = ctk.CTkButton(
            self,
            text="✅ Kodu Onayla",
            width=250,
            height=35,
            font=("Arial", 14, "bold"),
            fg_color=ALTIN_SARISI,
            text_color=SIYAH,
            hover_color="#DAA520",
            command=self._kod_onayla,
            state="disabled"
        )
        self.onayla_btn.pack(pady=10)

        # Hedef Grup
        ctk.CTkLabel(self, text="Hedef Grup/Kanal ID:", font=("Arial", 12), text_color=ALTIN_SARISI).pack(pady=(15, 5))
        self.grup_entry = ctk.CTkEntry(
            self,
            width=400,
            height=35,
            fg_color=SIYAH,
            border_color=ALTIN_SARISI,
            text_color=ALTIN_SARISI,
            placeholder_text="-100123456789"
        )
        self.grup_entry.pack(pady=5)

        # Mesaj
        ctk.CTkLabel(self, text="Gönderilecek Mesaj:", font=("Arial", 12), text_color=ALTIN_SARISI).pack(pady=(15, 5))
        self.mesaj_entry = ctk.CTkTextbox(
            self,
            width=400,
            height=80,
            fg_color=SIYAH,
            border_color=ALTIN_SARISI,
            text_color=ALTIN_SARISI
        )
        self.mesaj_entry.pack(pady=5)

        # Başlat/Durdur Butonu
        self.basla_btn = ctk.CTkButton(
            self,
            text="🚀 Gönderimi Başlat",
            width=300,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color="#00AA00",
            text_color="#FFFFFF",
            hover_color="#008800",
            command=self._gonderim_baslat,
            state="disabled"
        )
        self.basla_btn.pack(pady=20)

        # Durum
        self.durum_label = ctk.CTkLabel(
            self,
            text="⏳ Lütfen giriş yapın",
            font=("Arial", 13),
            text_color=ALTIN_SARISI,
            wraplength=550
        )
        self.durum_label.pack(pady=10)

    def _giris_yap(self):
        """Telegram'a giriş yap - Kod gönder"""
        telefon = self.telefon_entry.get().strip()
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()

        if not telefon or not api_id or not api_hash:
            self._durum_guncelle("⚠️ Lütfen tüm API bilgilerini ve telefon numarasını girin!", "#FF0000")
            return

        self.giris_btn.configure(state="disabled", text="🔄 Bağlanıyor...")
        self._durum_guncelle("🔄 Telegram'a bağlanılıyor...", ALTIN_SARISI)

        threading.Thread(target=self._giris_thread, args=(api_id, api_hash, telefon), daemon=True).start()

    def _giris_thread(self, api_id: str, api_hash: str, telefon: str):
        """Arka planda giriş işlemi"""
        try:
            # Client oluştur
            self.client = Client(
                SESSION_FILE,
                api_id=int(api_id),
                api_hash=api_hash,
                phone_number=telefon,
                in_memory=False
            )

            # Manuel bağlan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(self._async_giris(telefon))

        except PhoneNumberInvalid:
            self.after(100, lambda: self._giris_hata("❌ Geçersiz telefon numarası!"))
        except Exception as e:
            self.after(100, lambda: self._giris_hata(f"❌ Bağlantı hatası: {str(e)}"))

    async def _async_giris(self, telefon: str):
        """Async giriş işlemi"""
        await self.client.connect()

        # Oturum kontrolü
        if await self.client.is_user_authorized():
            self.after(100, lambda: self._giris_basarili(kod_gerekli=False))
            return

        # Kod gönder
        sent_code = await self.client.send_code(telefon)
        self.phone_code_hash = sent_code.phone_code_hash

        self.after(100, lambda: self._giris_basarili(kod_gerekli=True))

    def _giris_basarili(self, kod_gerekli: bool):
        """Giriş başarılı - UI güncelle"""
        if kod_gerekli:
            self._durum_guncelle("✅ Kod gönderildi! Telefonunuzu kontrol edin.", "#00FF00")
            self.giris_btn.configure(state="normal", text="🔑 Giriş Yap (Kod Gönder)")
            self.onayla_btn.configure(state="normal")
        else:
            self._durum_guncelle("✅ Zaten oturum açık! Mesaj gönderebilirsiniz.", "#00FF00")
            self.giris_btn.configure(state="normal", text="🔑 Giriş Yap (Kod Gönder)")
            self.onayla_btn.configure(state="disabled")
            self.basla_btn.configure(state="normal")

    def _giris_hata(self, mesaj: str):
        """Giriş hatası - UI güncelle"""
        self._durum_guncelle(mesaj, "#FF0000")
        self.giris_btn.configure(state="normal", text="🔑 Giriş Yap (Kod Gönder)")

    def _kod_onayla(self):
        """Onay kodunu doğrula"""
        kod = self.kod_entry.get().strip()

        if not kod:
            self._durum_guncelle("⚠️ Lütfen onay kodunu girin!", "#FF0000")
            return

        if not self.phone_code_hash:
            self._durum_guncelle("❌ Önce giriş yapmalısınız!", "#FF0000")
            return

        self.onayla_btn.configure(state="disabled", text="🔄 Doğrulanıyor...")
        self._durum_guncelle("🔄 Kod doğrulanıyor...", ALTIN_SARISI)

        threading.Thread(target=self._kod_onayla_thread, args=(kod,), daemon=True).start()

    def _kod_onayla_thread(self, kod: str):
        """Arka planda kod onaylama"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(self._async_kod_onayla(kod))

        except PhoneCodeInvalid:
            self.after(100, lambda: self._kod_hata("❌ Geçersiz kod!"))
        except SessionPasswordNeeded:
            self.after(100, lambda: self._kod_hata("❌ 2FA aktif! Şu an desteklenmiyor."))
        except Exception as e:
            self.after(100, lambda: self._kod_hata(f"❌ Hata: {str(e)}"))

    async def _async_kod_onayla(self, kod: str):
        """Async kod onaylama"""
        telefon = self.telefon_entry.get().strip()
        await self.client.sign_in(telefon, self.phone_code_hash, kod)

        self.after(100, lambda: self._kod_basarili())

    def _kod_basarili(self):
        """Kod onayı başarılı"""
        self._durum_guncelle("✅ Giriş başarılı! Mesaj gönderebilirsiniz.", "#00FF00")
        self.onayla_btn.configure(state="disabled", text="✅ Onaylandı")
        self.basla_btn.configure(state="normal")

    def _kod_hata(self, mesaj: str):
        """Kod onay hatası"""
        self._durum_guncelle(mesaj, "#FF0000")
        self.onayla_btn.configure(state="normal", text="✅ Kodu Onayla")

    def _gonderim_baslat(self):
        """Mesaj gönderimini başlat/durdur"""
        if not self.calisma_durumu:
            grup_id = self.grup_entry.get().strip()
            mesaj = self.mesaj_entry.get("1.0", "end").strip()

            if not grup_id or not mesaj:
                self._durum_guncelle("⚠️ Lütfen grup ID ve mesaj girin!", "#FF0000")
                return

            try:
                grup_id = int(grup_id)
            except ValueError:
                self._durum_guncelle("⚠️ Geçersiz grup ID!", "#FF0000")
                return

            self.calisma_durumu = True
            self.basla_btn.configure(text="⏸️ Durdur", fg_color="#AA0000", hover_color="#880000")

            threading.Thread(target=self._gonderim_thread, args=(grup_id, mesaj), daemon=True).start()
        else:
            self.calisma_durumu = False
            self.basla_btn.configure(text="🚀 Gönderimi Başlat", fg_color="#00AA00", hover_color="#008800")
            self._durum_guncelle("⏸️ Durduruldu.", ALTIN_SARISI)

    def _gonderim_thread(self, grup_id: int, mesaj: str):
        """Arka planda mesaj gönderimi"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self._async_gonderim(grup_id, mesaj))

    async def _async_gonderim(self, grup_id: int, mesaj: str):
        """Async mesaj gönderimi"""
        try:
            gonderilen_sayisi = 0
            toplam_uye = 0

            self.after(100, lambda: self._durum_guncelle("🔄 Grup üyeleri alınıyor...", ALTIN_SARISI))

            async for member in self.client.get_chat_members(grup_id):
                toplam_uye += 1

                if not self.calisma_durumu:
                    break

                user_id = member.user.id

                # Hafıza kontrolü
                if self.hafiza.kontrol(user_id):
                    continue

                # Bot kontrolü
                if member.user.is_bot:
                    continue

                try:
                    # Mesaj gönder
                    await self.client.send_message(user_id, mesaj)
                    gonderilen_sayisi += 1
                    self.hafiza.kaydet(user_id)

                    self.after(100, lambda g=gonderilen_sayisi, t=toplam_uye:
                              self._durum_guncelle(f"✅ {g} mesaj gönderildi (Toplam üye: {t})", "#00FF00"))

                    # Random bekleme (60-90 saniye)
                    bekleme_suresi = random.randint(60, 90)
                    for i in range(bekleme_suresi):
                        if not self.calisma_durumu:
                            break
                        kalan = bekleme_suresi - i
                        self.after(100, lambda k=kalan, g=gonderilen_sayisi:
                                  self._durum_guncelle(f"⏳ Sonraki mesaja {k} saniye... (Gönderilen: {g})", ALTIN_SARISI))
                        await asyncio.sleep(1)

                except FloodWait as e:
                    # FloodWait yönetimi
                    bekleme = e.value
                    self.after(100, lambda b=bekleme:
                              self._durum_guncelle(f"⚠️ FloodWait! {b} saniye bekleniyor...", "#FFA500"))
                    await asyncio.sleep(bekleme)

                except Exception as e:
                    print(f"Mesaj gönderme hatası ({user_id}): {e}")
                    continue

            self.after(100, lambda g=gonderilen_sayisi:
                      self._durum_guncelle(f"✅ Tamamlandı! Toplam {g} mesaj gönderildi.", "#00FF00"))
            self.after(100, lambda: self.basla_btn.configure(
                text="🚀 Gönderimi Başlat",
                fg_color="#00AA00",
                hover_color="#008800"
            ))
            self.calisma_durumu = False

        except Exception as e:
            self.after(100, lambda: self._durum_guncelle(f"❌ Hata: {str(e)}", "#FF0000"))
            self.after(100, lambda: self.basla_btn.configure(
                text="🚀 Gönderimi Başlat",
                fg_color="#00AA00",
                hover_color="#008800"
            ))
            self.calisma_durumu = False

    def _durum_guncelle(self, mesaj: str, renk: str):
        """Durum mesajını güncelle"""
        self.durum_label.configure(text=mesaj, text_color=renk)


# ==================== MAIN ====================
def main():
    """Ana program"""
    # 1. Lisans kontrolü
    lisans_ekrani = LisansEkrani()
    lisans_ekrani.mainloop()

    if not lisans_ekrani.lisans_gecerli:
        print("Lisans doğrulanamadı. Program kapatılıyor.")
        return

    # 2. Ana uygulama
    app = TelegramUserbotGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
