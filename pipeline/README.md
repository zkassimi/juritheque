# LexBase PDF Pipeline

Automatically extracts, structures, and uploads legal PDFs to Supabase.

## Setup (one time)

### 1. Install Python dependencies
```bash
cd pipeline
pip install -r requirements.txt
```

### 2. Configure .env
Edit `pipeline/.env` and fill in:
- `ANTHROPIC_API_KEY` — from console.anthropic.com
- `SUPABASE_SERVICE_KEY` — from Supabase Dashboard → Settings → API → service_role key

### 3. Create Supabase storage bucket
Run `setup_storage.sql` in your Supabase SQL Editor.

---

## Usage

### Process all PDFs in the pdfs/ folder
```bash
python extract.py
```

### Process a single file
```bash
python extract.py my_law.pdf
```

### Dry run (preview only, no DB writes)
```bash
python extract.py --dry-run
```

---

## How it works

```
pdfs/your_law.pdf
       ↓
[1] Extract text    — pdfplumber + PyMuPDF
       ↓
[2] Claude API      — identifies type, domain, title FR+AR,
                      articles, tags, date, status
       ↓
[3] Supabase Storage — uploads PDF, gets public URL
       ↓
[4] Supabase DB     — inserts into laws table
       ↓
[5] Rename + move   — pdfs/done/2024_Dahir_Code_de_la_Famille.pdf
```

## Folder structure
```
pipeline/
├── pdfs/           ← Drop your PDFs here
│   ├── done/       ← Successfully processed
│   └── errors/     ← Failed (check the report)
├── extract.py      ← Main script
├── requirements.txt
├── .env            ← Your API keys
└── setup_storage.sql
```

## Tips
- For **scanned PDFs** (images only), text extraction will fail. 
  Use Adobe Acrobat or an OCR tool (e.g. tesseract) to convert first.
- Process **100 PDFs** takes ~15-20 minutes and costs ~$0.50 in Claude API.
- The script **skips duplicates** by checking existing law numbers.
