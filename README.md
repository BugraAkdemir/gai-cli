# gai-cli (Gemini AI CLI)

`gai-cli`, Google Gemini API'sini terminale taşıyan, profesyonel, hızlı ve akıllı bir komut satırı aracıdır. Hem doğrudan soru sorabilir hem de projeniz üzerinde otomatik değişiklikler yapabilen gelişmiş bir "Agent" moduna sahiptir.

## ✨ Özellikler

- 🤖 **Agent Modu**: Projenizdeki dosyaları analiz eder, istediğiniz değişiklikleri (kod yazma, dosya oluşturma, silme, taşıma) planlar ve onayınızla uygular.
- 💬 **İnteraktif Sohbet**: Çok modlu sohbet arayüzü ile Gemini ile akıcı bir şekilde iletişim kurun.
- 📁 **Context Injection (@)**: `@dosya.py` veya `@src/` kullanarak dosyalarınızı sohbete bağlam olarak ekleyin.
- 🎨 **Premium UI**: `rich` kütüphanesi ile renklendirilmiş, şık ve okunabilir çıktı.
- 🌍 **Çok Dilli Destek**: Türkçe ve İngilizce dil seçenekleri.
- 🔒 **Güvenli İşlemler**: Dosya sistemi operasyonları proje dizini ile sınırlıdır.

## 🚀 Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/bugraakdemir/gai-cli.git
   cd gai-cli
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   pip install -e .
   ```

3. Kurulumu tamamlayın:
   ```bash
   gai setup
   ```

## 🛠️ Kullanım

### Tek Seferlik Soru
```bash
gai "Python'da liste üreteçleri (list comprehensions) nedir?"
```

### İnteraktif Mod (Sohbet & Agent)
Sadece `gai` yazarak interaktif modu başlatın:
```bash
gai
```
