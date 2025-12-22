import asyncio, os, random, threading, time, json
import customtkinter as ctk
from pyrogram import Client, errors
from tkinter import messagebox, simpledialog

# --- KONFİGÜRASYON ---
VERSION = "V2.1 NO-CRYPTO"
BASE_DIR = os.getcwd()
SESSION_DIR = os.path.join(BASE_DIR, "sessions")
ACCOUNTS_FILE = "accounts.json"
SABLON_FILE = "sablonlar.json"
SENT_USERS_FILE = "gonderilenler.txt"

# Klasör kontrolü
if not os.path.exists(SESSION_DIR): os.makedirs(SESSION_DIR)

API_ID = 30770812
API_HASH = "e6ed809073297c004b0781630f3a15d0"

GOLD, DARK_GOLD = "#FFD700", "#B8860B"
BG_BLACK, PANEL_BLACK = "#000000", "#0A0A0A"

class ErcuCommanderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"⚜️ ERCÜ ABİ TELEGRAM COMMANDER {VERSION} ⚜️")
        self.geometry("1150x850")
        self.configure(fg_color=BG_BLACK)

        self.accounts = self.load_json(ACCOUNTS_FILE, {})
        self.sablonlar = self.load_json(SABLON_FILE, ["Selam kuzen, bol kazançlar!"])
        self.sent_users = self.load_sent_users()

        self.active_client = None
        self.phone_code_hash = None
        self.selected_phone = None
        self.is_running = False
        self.loop = asyncio.new_event_loop()

        self.setup_ui()
        threading.Thread(target=self.run_loop, daemon=True).start()

    def load_json(self, path, default):
        if not os.path.exists(path): return default
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return default

    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

    def load_sent_users(self):
        if not os.path.exists(SENT_USERS_FILE): return set()
        with open(SENT_USERS_FILE, "r", encoding="utf-8") as f: return set(line.strip() for line in f)

    def setup_ui(self):
        # --- SOL PANEL (HESAP YÖNETİMİ) ---
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=PANEL_BLACK, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=2, pady=2)

        ctk.CTkLabel(self.sidebar, text="📱 HESAP YÖNETİMİ", font=("Impact", 22), text_color=GOLD).pack(pady=20)

        self.acc_list_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.acc_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(self.sidebar, text="+ HESAP EKLE", fg_color=DARK_GOLD, text_color="black", font=("Arial", 12, "bold"), command=self.add_account_ui).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.sidebar, text="📡 KOD İSTE", fg_color="#111", border_width=1, border_color=GOLD, text_color=GOLD, command=self.request_otp_ui).pack(fill="x", padx=20, pady=5)

        # --- ANA PANEL ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=25, pady=20)

        # Üst Panel
        info_frame = ctk.CTkFrame(self.main_area, fg_color=PANEL_BLACK, height=80)
        info_frame.pack(fill="x", pady=(0, 20))
        self.stat_label = ctk.CTkLabel(info_frame, text="Durum: Seçim Bekleniyor | Hafıza: " + str(len(self.sent_users)), font=("Arial", 14, "bold"), text_color=GOLD)
        self.stat_label.pack(pady=25)

        # Girişler
        input_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        input_frame.pack(fill="x")

        self.group_in = self.add_input(input_frame, "HEDEF GRUP", "Örn: slot_grubu")
        self.code_in = self.add_input(input_frame, "ONAY KODU (İlk Girişte)", "12345")
        self.proxy_in = self.add_input(input_frame, "PROXY (ip:port:user:pass)", "Opsiyonel")

        ctk.CTkLabel(self.main_area, text="MESAJ METNİ", font=("Arial", 12, "bold"), text_color=DARK_GOLD).pack(anchor="w", pady=(10,0))
        self.msg_entry = ctk.CTkTextbox(self.main_area, height=120, fg_color=PANEL_BLACK, border_width=1, border_color="#333")
        self.msg_entry.pack(fill="x", pady=5)

        # İşlem Butonları
        btn_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        self.start_btn = ctk.CTkButton(btn_frame, text="OPERASYONU BAŞLAT 🚀", fg_color="#1B5E20", height=50, font=("Arial", 15, "bold"), command=self.run_op_ui)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkButton(btn_frame, text="🛑 DURDUR", fg_color="#B71C1C", height=50, command=self.stop_op).pack(side="left", expand=True, fill="x", padx=5)

        # Log
        self.log_box = ctk.CTkTextbox(self.main_area, height=250, fg_color="#050505", font=("Consolas", 12), text_color="#00FF00")
        self.log_box.pack(fill="both", expand=True)

        self.refresh_acc_list()

    def add_input(self, master, label, holder):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(f, text=label, font=("Arial", 11, "bold"), text_color=DARK_GOLD).pack(anchor="w")
        e = ctk.CTkEntry(f, placeholder_text=holder, fg_color=PANEL_BLACK, border_color="#333", height=35)
        e.pack(fill="x"); return e

    def refresh_acc_list(self):
        for w in self.acc_list_frame.winfo_children(): w.destroy()
        for phone in self.accounts:
            color = "#1A1A1A" if phone != self.selected_phone else "#2E2E00"
            f = ctk.CTkFrame(self.acc_list_frame, fg_color=color, border_width=1, border_color="#333")
            f.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(f, text=f"📱 {phone}", font=("Arial", 11)).pack(side="left", padx=8, pady=5)
            ctk.CTkButton(f, text="SEÇ", width=40, height=22, command=lambda p=phone: self.select_acc(p)).pack(side="right", padx=2)
            ctk.CTkButton(f, text="X", width=25, height=22, fg_color="#440000", command=lambda p=phone: self.del_acc(p)).pack(side="right", padx=2)

    def select_acc(self, phone):
        self.selected_phone = phone
        self.refresh_acc_list()
        self.log(f"🎯 Hesap Seçildi: {phone}")
        self.stat_label.configure(text=f"Aktif Hesap: {phone}")

    def add_account_ui(self):
        num = simpledialog.askstring("Yeni Hesap", "Telefon No (+90...):")
        if num:
            self.accounts[num] = {"proxy": ""}
            self.save_json(ACCOUNTS_FILE, self.accounts)
            self.refresh_acc_list()
            self.log(f"✅ {num} listeye alındı.")

    def request_otp_ui(self):
        self.start_task(self.request_otp())

    async def request_otp(self):
        if not self.selected_phone:
            self.log("⚠️ Önce bir hesap seç!")
            return

        client = None
        try:
            self.log(f"📡 {self.selected_phone} için kod isteniyor...")
            client = Client(
                name=os.path.join(SESSION_DIR, self.selected_phone),
                api_id=API_ID,
                api_hash=API_HASH
            )
            await client.connect()

            res = await client.send_code(self.selected_phone)
            self.phone_code_hash = res.phone_code_hash
            self.log("📩 Kod gönderildi! 'ONAY KODU' kutusuna yazıp BAŞLAT de.")

        except Exception as e:
            self.log(f"❌ Kod İsteme Hatası: {str(e)}")
        finally:
            if client:
                try:
                    await client.disconnect()
                except:
                    pass

    def run_op_ui(self):
        self.start_task(self.run_op())

    async def run_op(self):
        if self.is_running:
            self.log("⚠️ Operasyon zaten çalışıyor!")
            return

        if not self.selected_phone:
            self.log("⚠️ Önce bir hesap seç!")
            return

        self.is_running = True
        client = None

        try:
            client = Client(
                name=os.path.join(SESSION_DIR, self.selected_phone),
                api_id=API_ID,
                api_hash=API_HASH
            )
            await client.connect()

            # Oturum Kontrolü / Giriş
            me = None
            try:
                me = await client.get_me()
            except:
                pass

            if not me:
                code = self.code_in.get().strip()
                if not code:
                    self.log("⚠️ Önce KOD İSTE ve gelen kodu yaz!")
                    self.is_running = False
                    return

                if not self.phone_code_hash:
                    self.log("⚠️ Önce 'KOD İSTE' butonuna bas!")
                    self.is_running = False
                    return

                try:
                    await client.sign_in(self.selected_phone, self.phone_code_hash, code)
                    self.log("✅ Giriş başarılı!")
                except Exception as e:
                    self.log(f"❌ Giriş hatası: {str(e)}")
                    self.is_running = False
                    return

            target = self.group_in.get().strip()
            if not target:
                self.log("⚠️ Hedef grup girilmedi!")
                self.is_running = False
                return

            # @ işaretini kaldır
            target = target.replace("@", "")

            msg_base = self.msg_entry.get("1.0", "end-1c").strip()
            if not msg_base:
                self.log("⚠️ Mesaj metni boş!")
                self.is_running = False
                return

            self.log(f"🚀 Operasyon başlıyor... Hedef: {target}")
            count = 0

            # Grup üyelerini al
            try:
                async for member in client.get_chat_members(target):
                    if not self.is_running:
                        self.log("🛑 Operasyon kullanıcı tarafından durduruldu.")
                        break

                    # Bot kontrolü
                    if member.user.is_bot:
                        continue

                    uid = str(member.user.id)

                    # Daha önce gönderildi mi kontrol et
                    if uid in self.sent_users:
                        continue

                    # Anti-Spam Görünmez Karakter
                    final_msg = f"{msg_base}\n\u200c" + "".join(random.choices([" ", "\u200b", "\u200c"], k=3))

                    try:
                        await client.send_message(member.user.id, final_msg)
                        self.sent_users.add(uid)

                        # Dosyaya kaydet
                        with open(SENT_USERS_FILE, "a", encoding="utf-8") as f:
                            f.write(uid + "\n")

                        count += 1
                        user_name = member.user.first_name or "Bilinmeyen"
                        self.log(f"✈️ Gönderildi: {user_name} ({count})")

                        # Hafıza güncelle
                        self.stat_label.configure(text=f"Aktif: {self.selected_phone} | Gönderilen: {count} | Hafıza: {len(self.sent_users)}")

                        # Rastgele bekleme (65-95 saniye)
                        wait_time = random.randint(65, 95)
                        await asyncio.sleep(wait_time)

                    except errors.FloodWait as e:
                        self.log(f"⏳ Flood kontrolü! {e.value} saniye bekleniyor...")
                        await asyncio.sleep(e.value + 5)

                    except errors.PeerFlood:
                        self.log("❌ Peer Flood! Hesap geçici olarak kısıtlandı. Başka hesap dene.")
                        break

                    except errors.UserPrivacyRestricted:
                        self.log(f"⚠️ Kullanıcı mesaj almayı kapatmış, atlanıyor...")
                        continue

                    except Exception as e:
                        error_msg = str(e)
                        if "chat write forbidden" in error_msg.lower():
                            self.log(f"⚠️ Kullanıcıya mesaj gönderilemedi (gizlilik), atlanıyor...")
                        else:
                            self.log(f"⚠️ Hata: {error_msg[:60]}...")
                        await asyncio.sleep(5)
                        continue

            except errors.ChatAdminRequired:
                self.log("❌ Bu grubun üyelerini listelemek için admin yetkisi gerekli!")
            except Exception as e:
                self.log(f"❌ Grup üyeleri alınamadı: {str(e)}")

            self.log(f"🏁 Operasyon tamamlandı. Toplam {count} mesaj gönderildi.")

        except Exception as e:
            self.log(f"❌ Kritik Hata: {str(e)}")

        finally:
            self.is_running = False
            if client:
                try:
                    await client.disconnect()
                except:
                    pass

    def log(self, text):
        ts = time.strftime('%H:%M:%S')
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] » {text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def stop_op(self):
        self.is_running = False
        self.log("🛑 Durduruluyor...")

    def run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_task(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def del_acc(self, p):
        if messagebox.askyesno("Onay", f"{p} silinsin mi?"):
            del self.accounts[p]
            self.save_json(ACCOUNTS_FILE, self.accounts)
            if self.selected_phone == p:
                self.selected_phone = None
            self.refresh_acc_list()
            self.log(f"🗑️ {p} silindi.")

    def show_report(self):
        messagebox.showinfo("Rapor", f"Toplam Hafıza: {len(self.sent_users)} kişi.")

if __name__ == "__main__":
    try:
        app = ErcuCommanderApp()
        app.mainloop()
    except Exception as e:
        print(f"Uygulama başlatma hatası: {e}")
        input("Çıkmak için Enter'a bas...")
