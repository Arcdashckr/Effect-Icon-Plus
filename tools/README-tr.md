<a alt="English" href="/README.md" target="_blank" style="text-decoration: none">
  <img src="https://img.shields.io/badge/language-English-blue?style=flat">
</a>
&nbsp;
<a alt="Turkish" href="/README-tr.md" target="_blank" style="text-decoration: none">
  <img src="https://img.shields.io/badge/language-Turkish-red?style=flat">
</a>

# 🛠️ Effect-Icon-Plus Geliştirici Araç Kiti

Bu klasör, **Effect-Icon-Plus** kaynak paketine yeni mod destekleri eklemek, renk paletlerini yönetmek ve reponun vitrin görselleri ile dökümantasyonunu otomatik olarak güncellemek için geliştirilmiş Python tabanlı bir otomasyon stüdyosudur.

Tüm süreçler ImageMagick kütüphanesi ve Python scriptleri ile tıkır tıkır işleyecek şekilde birbirine bağlanmıştır.

---

## 🚀 Hızlı Başlangıç

Tüm araç kitini tek bir panelden yönetmek için klasör içindeki **`start.bat`** dosyasını çift tıklayarak çalıştırmanız yeterlidir. Karşınıza şu entegre menü gelecektir:

- [1] Modlardan İkonları Ayıkla ve Büyüt (Extract ve Scale)
- [2] Renk Paletine Göre Çerçevele ve Birleştir (Merge)
- [3] Önizleme Gridi Oluştur (Display Grid)
- [4] Çıkış

---

## 📦 Adım Adım İş Akışı ve Dosya Görevleri

### 1️⃣ Adım 1: İkon Ayıklama (extract_and_scale.py)
* **Görevi:** İndirdiğin mod dosyalarının `.jar` veya `.zip` içerisindeki efekt ikonlarını otomatik olarak bulur.
* **Nasıl Çalışır?** Mod arşivini okur, içerisindeki `assets/<mod_id>/textures/mob_effect/` klasöründeki tüm 16x16 pixel-art ikonları yakalar. Bunları bulanıklaştırmadan (Nearest Neighbor) **54x54** boyutuna ölçekler ve `tools/extracted/<mod_id>/` klasörünün altına kaydeder.

### 2️⃣ Adım 2: Renk Analizi ve Çerçeveleme (merge_frames.py)
* **Görevi:** Ayıklanan ham ikonların renk paletini çıkarır, `colors.json` dosyasını besler ve 9 aşamalı renkli çerçeveleri (`frames/`) ikonla birleştirir.
* **Gelişmiş Özellikler:**
  * **Hız Filtresi:** Çalıştırıldığında size sorar. Eğer çıktı ikon zaten ana repoda varsa ve JSON değişmemişse o ikonu es geçerek muazzam bir zaman tasarrufu sağlar.
  * **Kontrast Çarpanı:** ImageMagick'in çıkardığı otomatik renklerin donuk/gri kalmasını önler, gradyan geçişlerini matematiksel olarak esneterek çerçeveleri daha canlı hale getirir.
  * **Çift Blok Yönetimi (colors.json):**
    * "auto": ImageMagick tarafından üretilen, çerçevenin 9 dilimine otomatik giydirilen el değmemiş referans blok.
    * "manual": Sizin düzenlemeleriniz için ayrılmış alan. Ayrıca efekt isminin sonuna eklenen `_all` anahtarı, resimdeki tüm benzersiz ham renkleri size palet referansı olarak sunar (boyamayı etkilemez).

### 3️⃣ Adım 3: Vitrin ve Dökümantasyon Otomasyonu (create_display.py)
* **Görevi:** Repoda biriken son 54x54 işlenmiş ikonları yan yana 10'arlı dizerek önizleme görselleri üretir, ana reponun dökümantasyonunu otomatik günceller.
* **Seçenekler:**
  1. *Sadece Vanilla:* `assets/minecraft` altını tarar, çıktı ismini `effect_display_vanilla.png` yapar.
  2. *Belirli Bir Mod:* Sadece girdiğiniz mod klasörünü basar.
  3. *Tüm Modlar Ayrı Ayrı:* Her mod için bağımsız görseller üretir.
  4. *Hepsini Tek Resimde Birleştir:* Sabit linklerinizin (`README.md` vb.) kırılmaması için Vanilla ve modları tek bir dev `effect_display_mod.png` görselinde birleştirir.
* **Gelişmiş Özellikler:**
  * **Kayıpsız Esnek Büyütme:** Sabit çözünürlüklere zorlayıp resmi kırpmak yerine, dikey boyutu ikon sayısına göre serbest bırakır ve pikselleri %400 (`_upscaled.png`) jilet gibi keskin büyüterek GitHub için harika bir vitrin sunar.
  * **Canlı README Entegrasyonu:** Ana repondaki `README.md` dosyasının tepesindeki Modrinth temalı özel istatistik rozetlerini (Badge) güncel mod ve ikon sayılarıyla otomatik yeniler.
  * **Otomatik `compatibility.md`:** Desteklenen modları ve içerdikleri ikon sayılarını alfabetik olarak tarayıp harika bir Markdown tablosu halinde kendi kendine derler.

---

## 🛠️ Gereksinimler

Araç kitinin eksiksiz çalışabilmesi için sisteminizde şunların kurulu ve ortam değişkenlerine (PATH) eklenmiş olması gerekir:
1. **Python 3.x**
2. **ImageMagick** (Konsoldan `magick` komutunun çalışabiliyor olması zorunludur.)

## 📁 Klasör Yapısı Referansı

- tools/
  - extracted/           # 1. adımdan çıkan 54x54 ham mod ikonları
  - frames/              # Çerçevenin 1.png'den 9.png'ye kadar olan beyaz dilimleri
  - start.bat            # Ana kontrol paneli
  - colors.json          # Renk veritabanı (auto/manual)
  - extract_and_scale.py # Mod ayıklayıcı script
  - merge_frames.py      # Akıllı renk işleyici ve çerçeveleyici script
  - create_display.py    # Vitrin, README ve tablo güncelleyici script