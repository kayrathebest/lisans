# Telegram Userbot - GUI Control

Sıfır konsol girişi gerektiren, tamamen GUI tabanlı Telegram Userbot uygulaması.

## Özellikler

✅ **Sıfır Konsol Girişi**: Tüm işlemler GUI üzerinden yapılır, terminal'den hiçbir şey istenmez
✅ **GitHub Lisans Sistemi**: Uygulama başlangıcında otomatik lisans doğrulama
✅ **Manuel Pyrogram Auth**: `client.connect()`, `client.send_code()`, `client.sign_in()` ile tam kontrol
✅ **Hafıza Sistemi**: Gönderilen kullanıcılar kaydedilir, tekrar mesaj gönderilmez
✅ **FloodWait Yönetimi**: Otomatik bekleme ve hata yönetimi
✅ **Random Gecikme**: 60-90 saniye arası rastgele bekleme
✅ **Modern UI**: Siyah-Altın sarısı tema ile CustomTkinter arayüzü

## Kurulum

### 1. Gerekli Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. API Bilgilerini Alın

1. https://my.telegram.org adresine gidin
2. "API development tools" bölümünden API ID ve API Hash alın

### 3. Uygulamayı Çalıştırın

```bash
python telegram_userbot.py
```

## Kullanım

### Adım 1: Lisans Doğrulama
- Uygulama açılınca lisans key'inizi girin
- GitHub'dan otomatik olarak lisans listesi kontrol edilir

### Adım 2: Telegram Girişi
1. API ID ve API Hash bilgilerinizi girin
2. Telefon numaranızı girin (+905551234567 formatında)
3. "Giriş Yap (Kod Gönder)" butonuna tıklayın
4. Telegram'dan gelen kodu "Onay Kodu" alanına girin
5. "Kodu Onayla" butonuna tıklayın

### Adım 3: Mesaj Gönderimi
1. Hedef grup/kanal ID'sini girin (örn: -100123456789)
2. Göndermek istediğiniz mesajı yazın
3. "Gönderimi Başlat" butonuna tıklayın

## Güvenlik Özellikleri

- **60-90 saniye** arası rastgele bekleme süresi
- **FloodWait** otomatik yönetimi
- **Hafıza sistemi** ile tekrarlı mesaj engelleme
- Bot kullanıcıları otomatik atlanır

## Dosyalar

- `telegram_userbot.py` - Ana uygulama
- `gonderilenler.txt` - Gönderilen kullanıcı ID'leri (otomatik oluşturulur)
- `userbot_session.session` - Pyrogram oturum dosyası (otomatik oluşturulur)

## Önemli Notlar

⚠️ **TgCrypto**: Uygulama TgCrypto olmadan çalışır, uyarı mesajı otomatik kapatılır
⚠️ **2FA**: Şu anda iki faktörlü kimlik doğrulama desteklenmemektedir
⚠️ **Konsol**: Hiçbir terminal girişi gerekmez, tüm işlemler GUI üzerinden yapılır

## Teknik Detaylar

### Manuel Pyrogram Authentication
```python
# client.start() kullanılmaz!
await client.connect()
sent_code = await client.send_code(phone_number)
await client.sign_in(phone_number, phone_code_hash, code)
```

### FloodWait Yönetimi
```python
try:
    await client.send_message(user_id, message)
except FloodWait as e:
    await asyncio.sleep(e.value)
```

### Hafıza Sistemi
```python
if not hafiza.kontrol(user_id):
    await client.send_message(user_id, message)
    hafiza.kaydet(user_id)
```

## Lisans

Bu proje GitHub tabanlı lisans sistemi kullanır. Lisans anahtarı gereklidir.

---

**Geliştirici:** Claude AI
**Versiyon:** 1.0.0
**Tarih:** 2025
