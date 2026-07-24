<a alt="English" href="/README.md" target="_blank" style="text-decoration: none">
  <img src="https://img.shields.io/badge/language-English-blue?style=flat">
</a>
&nbsp;
<a alt="Turkish" href="/README-tr.md" target="_blank" style="text-decoration: none">
  <img src="https://img.shields.io/badge/language-Turkish-red?style=flat">
</a>

# 🛠️ Effect-Icon-Plus Geliştirici Araç Kiti

Bu klasör; Modrinth üzerinden mod/koleksiyon indirmek, modların metadatalarını kontrol edip önbelleğe almak, **Effect-Icon-Plus** kaynak paketine yeni mod destekleri eklemek, renk paletlerini yönetmek ve reponun vitrin görselleri ile dökümantasyonunu otomatik olarak güncellemek için geliştirilmiş Python tabanlı bir otomasyon stüdyosudur.

Tüm süreçler ImageMagick kütüphanesi ve Python scriptleri ile tıkır tıkır işleyecek şekilde birbirine bağlanmıştır.

---

## 🚀 Hızlı Başlangıç

Tüm araç kitini tek bir panelden yönetmek için klasör içindeki **`start.bat`** dosyasını çift tıklayarak çalıştırmanız yeterlidir. Karşınıza şu entegre menü gelecektir:

- [1] Mod veya Koleksiyon İndir
- [2] Modlardan İkonları Ayıkla ve Büyüt
- [3] Renk Paletine Göre Çerçevele ve Birleştir
- [4] Önizleme Gridi Oluştur
- [5] Depo Dosyalarını Üret (stats.json, compatibility.md)
- [6] Tam Pipeline Çalıştır
- [7] Geçici Dosyaları Temizle
- [8] Çıkış

---

## 📦 Adım Adım İş Akışı ve Dosya Görevleri

### 0️⃣ Adım 0: İndirici ve Metadata Yöneticisi (collection_downloader.py & metadata_manager.py)
* **collection_downloader.py**:
  * Modrinth koleksiyonlarını veya tek bir modu slug/link kullanarak indirir.
  * Sadece içerisinde efekt ikonu barındıran modları saklar (indirme sonrası JAR içinde `mob_effect` textures klasörü olup olmadığını kontrol eder, yoksa modu siler).
  * Metadata güncelleme adımlarını dinamik olarak tetikler.
* **metadata_manager.py**:
  * JAR dosyalarından namespace'leri ayıklar ve `mod_metadata.json` yazar/ikon/sayfa linki önbelleğini yönetir.
  * İnteraktif konsol eşleştirme arayüzü sunar: Eğer bir modun namespace adı Modrinth slug'ı ile doğrudan eşleşmiyorsa Modrinth üzerinde arama yapar, en olası sonuçları listeler ve kullanıcıdan doğru olanı seçmesini, manuel slug girmesini veya modu pas geçmesini ister.

### 1️⃣ Adım 1: İkon Ayıklama (extract_and_scale.py)
* **Görevi:** `tools/mods/` klasöründeki mod arşivlerinin içerisindeki efekt ikonlarını otomatik olarak bulur.
* **Nasıl Çalışır?** Mod arşivini okur, `assets/<mod_id>/textures/mob_effect/` klasöründeki tüm 16x16 pixel-art ikonları yakalar, bunları piksel kaybı olmadan (Nearest Neighbor) **36x36** boyutuna ölçekler ve `tools/extracted/<mod_id>/` klasörünün altına kaydeder.

### 2️⃣ Step 2: Renk Analizi ve Çerçeveleme (merge_frames.py)
* **Görevi:** Ayıklanan ham ikonların renk paletini çıkarır, `colors.json` dosyasını besler ve 9 aşamalı renkli çerçeveleri (`frames/`) ikonla birleştirir.
* **Gelişmiş Özellikler:**
  * **Hız Filtresi:** Çalıştırıldığında size sorar. Eğer çıktı ikon zaten ana repoda varsa ve JSON değişmemişse o ikonu es geçerek muazzam bir zaman tasarrufu sağlar.
  * **Kontrast Çarpanı:** ImageMagick'in çıkardığı otomatik renklerin donuk/gri kalmasını önler, gradyan geçişlerini matematiksel olarak esneterek çerçeveleri daha canlı hale verir.
  * **Çift Blok Yönetimi (colors.json):**
    * "auto": ImageMagick tarafından üretilen, çerçevenin 9 dilimine otomatik giydirilen el değmemiş referans blok.
    * "manual": Sizin düzenlemeleriniz için ayrılmış alan. Ayrıca efekt isminin sonuna eklenen `_all` anahtarı, resimdeki tüm benzersiz ham renkleri size palet referansı olarak sunar (boyamayı etkilemez).

### 3️⃣ Adım 3: Önizleme Otomasyonu (create_display.py)
* **Görevi:** Ana repodaki son 54x54 işlenmiş ikonları yan yana 10'arlı dizerek önizleme görselleri üretir.
* **Seçenekler:**
  1. *Sadece Vanilla:* `assets/minecraft` altını tarar, çıktı ismini `effect_display_vanilla.png` yapar.
  2. *Belirli Bir Mod:* Sadece girdiğiniz mod klasörünü basar.
  3. *Tüm Modlar Ayrı Ayrı:* Her mod için bağımsız görseller üretir.
  4. *Hepsini Tek Resimde Birleştir:* Sabit linklerinizin kırılmaması için Vanilla ve modları tek bir dev `effect_display_mod.png` görselinde birleştirir.
* **Gelişmiş Özellikler:**
  * **Kayıpsız Esnek Büyütme:** Sabit çözünürlüklere zorlayıp resmi kırpmak yerine, dikey boyutu ikon sayısına göre serbest bırakır ve pikselleri %300 (`_upscaled.png`) jilet gibi keskin büyüterek GitHub için harika bir vitrin sunar.

### 4️⃣ Adım 4: Depo Belgeleri Güncelleyici (generate_repo_files.py)
* **Görevi:** Depo dökümantasyonunu ve metrikleri otomatik olarak yeniden oluşturur.
* **Çıktılar:**
  * **Canlı README Entegrasyonu (`stats.json`):** Ana repondaki `README.md` rozetleri için mod ve ikon sayılarını tutar.
  * **Otomatik `compatibility.md`:** Önbelleğe alınmış metadataları (`mod_metadata.json`) kullanarak alfabetik olarak desteklenen modlar tablosunu derler. Mod sayfalarına gitmek için `page_url` değerini kullanır.

### 5️⃣ Adım 5: Temizlik (clean_temp.py)
* **Görevi:** `tools/mods/` ve `tools/extracted/` klasörlerindeki geçici ve işi bitmiş dosyaları temizleyerek disk alanından tasarruf sağlar. Klasörlerdeki `.gitignore` dosyalarını korur.

---

## 🛠️ Gereksinimler

Araç kitinin eksiksiz çalışabilmesi için sisteminizde şunların kurulu ve ortam değişkenlerine (PATH) eklenmiş olması gerekir:
1. **Python 3.x**
2. **ImageMagick** (Konsoldan `magick` komutunun çalışabiliyor olması zorunludur.)

## 📁 Klasör Yapısı Referansı

- tools/
  - extracted/           # 1. adımdan çıkan 36x36 ham mod ikonları
  - frames/              # Çerçevenin 1.png'den 9.png'ye kadar olan beyaz dilimleri
  - mods/                # İndirilen jar/zip mod dosyaları
  - start.bat            # Ana kontrol paneli scripti
  - colors.json          # Renk veritabanı (auto/manual)
  - mod_metadata.json    # Mod metadata önbelleği
  - collection_downloader.py # Mod indirici script
  - metadata_manager.py  # Metadata yöneticisi script
  - extract_and_scale.py # Mod ayıklayıcı script
  - merge_frames.py      # Akıllı renk işleyici ve çerçeveleyici script
  - create_display.py    # Vitrin oluşturucu script
  - generate_repo_files.py # stats.json ve compatibility.md güncelleyici script
  - clean_temp.py        # Geçici dosyaları temizleme scripti