# Smart Expense Tracker with Huffman File Compression

A Python mini-project that combines a local expense tracker with a real Huffman Coding compression module for exported reports.

## Features

- Login and signup with hashed passwords
- Add, edit, delete, and search income/expense entries
- SQLite local database storage
- Category support for Food, Travel, Shopping, Bills, Health, Education, Salary, and Other
- Dashboard with total income, total expenses, balance, monthly spending, and category-wise chart
- Export reports as CSV or TXT
- Compress exported reports into `.bin` files using Huffman Coding
- Decompress `.bin` files back into readable reports
- Compression size and ratio display
- Light/dark mode toggle

## Tech Stack

- Python
- Tkinter
- SQLite
- Huffman Coding with `heapq`
- File handling with CSV, TXT, and binary files

## Project Architecture

```text
User Interface
       |
Expense Manager
       |
SQLite Database
       |
Report Generator
       |
Huffman Compressor
       |
Compressed File Storage
```

## Files

- `app.py` - Tkinter user interface and application flow
- `database.py` - SQLite tables and CRUD operations
- `reports.py` - TXT and CSV report generation
- `huffman.py` - Huffman compression and decompression logic
- `test_huffman.py` - Unit tests for compression round trips

## How To Run

```bash
python app.py
```

On Windows, you may need:

```bash
py app.py
```

## How To Test

```bash
python -m unittest test_huffman.py
```

## Huffman Coding Flow

```text
Read Report File
      |
Count Character Frequency
      |
Build Huffman Tree
      |
Generate Binary Codes
      |
Pack Bits into Bytes
      |
Save Metadata + Compressed Data in .bin File
```

Decompression reads the saved code metadata, rebuilds the reverse code map, decodes the bit stream, and restores the original report text.
