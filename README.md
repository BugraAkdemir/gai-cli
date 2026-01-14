# gai-ag (Gemini Autonomous Agent)

`gai-ag`, Google Gemini API'sini terminale taşıyan, profesyonel, hızlı ve akıllı bir komut satırı aracıdır. Hem doğrudan soru sorabilir hem de projeniz üzerinde otomatik değişiklikler yapabilen gelişmiş bir \"Agent\" moduna sahiptir.
- **Otonom Agent Modu**: Hataları kendi kendine düzeltir, testleri koşturur ve çözüm üretir.
- **Proje Hafızası (Brain)**: Her projede kendi `.gai/` klasörünü oluşturur; geçmişi, durumu ve hataları orada saklar.
- **Zeki Tarama**: Token tasarrufu için proje yapısını önbelleğe alır ve kritik dosyaları önceliklendirir.
- **Polyglot Desteği**: Flutter, Node.js ve Python projelerini otomatik algılar.

## ✨ Özellikler

- 🤖 **Agent Modu**: Projenizdeki dosyaları analiz eder, istediğiniz değişiklikleri (kod yazma, dosya oluşturma, silme, taşıma) planlar ve onayınızla uygular.
- 💬 **İnteraktif Sohbet**: Çok modlu sohbet arayüzü ile Gemini ile akıcı bir şekilde iletişim kurun.
- 📁 **Context Injection (@)**: `@dosya.py` veya `@src/` kullanarak dosyalarınızı sohbete bağlam olarak ekleyin.
- 🎨 **Premium UI**: `rich` kütüphanesi ile renklendirilmiş, şık ve okunabilir çıktı.
- 🌍 **Çok Dilli Destek**: Türkçe ve İngilizce dil seçenekleri.
- 🔒 **Güvenli İşlemler**: Dosya sistemi operasyonları proje dizini ile sınırlıdır.

## 🚀 Kurulum

### PyPI'den (En Kolay)
```bash
pip install gai-ag
```

### Geliştirme İçin
1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/bugraakdemir/gai-cli.git
   cd gai-cli
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   pip install -e .
   ```

## 🛠️ Kullanım

> **Not**: Terminal'den hem `gai` hem `gai-ag` komutu çalışır!

### Tek Seferlik Soru
```bash
gai "Python'da liste üreteçleri (list comprehensions) nedir?"
# veya
gai-ag "Python'da liste üreteçleri nedir?"
```

### İnteraktif Mod (Sohbet & Agent)
Sadece `gai` veya `gai-ag` yazarak interaktif modu başlatın:
```bash
gai
# veya
gai-ag
```
