# Johto War Campaign（中文資源）

[Pokémon: Legends of Sinnoh - Johto War Campaign](https://steamcommunity.com/sharedfiles/filedetails/?id=3274191922) 的中文卡牌／資料製作倉庫。

本倉庫提供：**中文 Cube**、**Card Generator 資產與腳本**、以及把牌組匯入 [Tabletop Simulator](https://store.steampowered.com/app/286160/Tabletop_Simulator/) 的流程說明。

---

## 致謝與翻譯

| 角色 | 名稱 |
|------|------|
| 原作戰役／模組 | [Aursiniuria](https://steamcommunity.com/id/Aursiniuria/myworkshopfiles/)（Workshop） |
| 規則書標註 | Levatius / Aursiniuria（Johto War Rulebook） |
| **中文翻譯** | **盤龍** |

本倉庫的中文 Cube、卡面文案與相關在地化內容由 **盤龍** 翻譯與整理。若轉載或再發布，請保留翻譯者署名。

原版英文模組：  
https://steamcommunity.com/sharedfiles/filedetails/?id=3274191922

---

## 目錄結構（精簡）

```
johto-war-campaign/
├── README.md                          ← 本說明
├── Card Generator/
│   ├── johto_cube.xlsx                ← 中文 Cube（產生器預設讀這個）
│   ├── johto_cube_ENG.xlsx            ← 英文對照 Cube
│   ├── Johto War Card Generator Guide.docx
│   ├── requirements.txt
│   ├── generator_assets/              ← 圖、字型、卡底、archetype 等
│   └── card_generator/                ← Python 腳本與 output/
│       ├── main_tm.py
│       ├── main_pokemon.py
│       ├── main_utility.py
│       ├── main_abilities.py
│       ├── main_tactics.py
│       ├── main_shrine.py
│       ├── main_legend.py
│       ├── main_trainer.py
│       ├── config.py
│       ├── utils.py
│       └── output/                    ← 產牌輸出（通常不提交）
└── tools/                             ← 輔助腳本（TTS 裁切、翻譯等）
```

**重要：** 資料夾層級請保持原樣，腳本靠相對路徑找資產與輸出位置。

---

## 環境安裝

### 1. Python

建議 **Python 3.10+**（本機亦可用虛擬環境）。

```powershell
cd E:\github\johto-war-campaign
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r "Card Generator\requirements.txt"
```

若還要用 TTS／PDF 輔助工具，可再裝：

```powershell
python -m pip install pymupdf deep-translator Pillow tqdm requests
```

### 2. 字型（中文卡面）

產生器會依文字內容自動改用 CJK 字型（如微軟雅黑／正黑）。請確認 Windows 有：

- `C:\Windows\Fonts\msyh.ttc`（雅黑）
- 可選：`msjh.ttc`（正黑）

路徑可在 `Card Generator/card_generator/config.py` 調整。

### 3.（可選）Anaconda

原版《Johto War Card Generator Guide》使用 Anaconda `py37` 環境。若你沿用該流程：

1. 安裝 [Anaconda](https://www.anaconda.com/)
2. 開 Anaconda Prompt，建立／啟用環境後  
   `cd` 到 `Card Generator\card_generator`
3. 再執行下方的 `python main_xxx.py`

---

## 如何產牌（Card Generator）

### 基本流程

1. 編輯 `Card Generator/johto_cube.xlsx`（或先改英文對照再同步）
2. 補齊 `generator_assets/` 缺圖（檔名須與 Cube 欄位一致）
3. 進入腳本目錄並執行對應 `main_*.py`
4. 在 TTS **Cloud Manager** 上傳 `output/.../decks/` 大圖
5. 把 Cloud URL 貼回腳本，產出 Deck Object JSON
6. JSON 放進 TTS **Saved Objects** 後匯入桌面

### 各類主腳本

在 `Card Generator\card_generator` 下執行：

| 腳本 | 產出內容 |
|------|----------|
| `python main_tm.py` | 招式／TM 牌 |
| `python main_pokemon.py` | 寶可夢牌 |
| `python main_abilities.py` | 特性牌 |
| `python main_tactics.py` | 戰術牌 |
| `python main_utility.py` | Utility／Fortune／Disaster／Quest／Gamble 等 |
| `python main_shrine.py` | 神社牌 |
| `python main_legend.py` | 傳說任務牌 |
| `python main_trainer.py` | 訓練家牌 |

範例：

```powershell
cd "Card Generator\card_generator"
..\..\.venv\Scripts\python.exe main_tm.py
```

### 輸出資料夾常見結構

每個類型的 `output/<類型>/` 大致包含：

| 子資料夾 | 內容 |
|----------|------|
| `card_fronts` | 單卡正面 |
| `card_backs` | 單卡背面 |
| `decks` | 10×7 牌組大圖（給 Cloud Manager） |
| `moves` | 招式／效果文字區塊圖 |
| `deck_object` | 給 TTS 匯入的 JSON |

---

## 上傳到 Tabletop Simulator（逐步）

> 詳細原文也見：`Card Generator/Johto War Card Generator Guide.docx` 的 **Importing the Decks**。

### A. 上傳牌圖到 Cloud（產生器必要步驟）

1. 跑完 `main_*.py`，腳本會停下來等 Cloud URL  
2. 開 TTS → 建立房間  
3. **Modding → Cloud Manager**  
4. 依需要建資料夾，上傳該類 `output/.../decks/` 的  
   `0a_deck.png`、`0a_back.png`、`1a_deck.png`…  
5. 複製每張圖的 **Cloud URL**，貼回終端機提示並按 Enter  
6. 腳本產出 `deck_object` 下的 JSON  

### B. 匯入 Saved Objects

1. 複製 JSON 到：  
   `Documents\My Games\Tabletop Simulator\Saves\Saved Objects`  
   （OneDrive 使用者常見路徑：  
   `%USERPROFILE%\OneDrive\Documents\My Games\Tabletop Simulator\Saves\Saved Objects`）  
2. TTS：**Objects → Saved Objects** → 選檔放到桌上  
3. **Games → Save & Play** 存下完整戰役桌面  

### C. 更新 Steam Workshop（可選）

Cloud Manager **只是圖床**，不是 Workshop 發布。

1. 載入已放好新牌的完整桌面  
2. **Modding → Workshop Upload**（或 Update）  
3. 選 **Update** 既有 item，或 **New** 發布自己的版本  
4. 填說明、可見性後上傳  

**注意：** 更新 [官方 Johto War Campaign](https://steamcommunity.com/sharedfiles/filedetails/?id=3274191922) 需要原作者帳號權限。一般翻譯／自用版請用自己的 Workshop item，並註明原作與翻譯者 **盤龍**。

### 本機模組常見路徑

| 用途 | 路徑 |
|------|------|
| TTS 使用者資料 | `...\My Games\Tabletop Simulator\` |
| Workshop JSON（訂閱後） | `...\Mods\Workshop\<WorkshopID>.json` |
| 圖／模型快取 | `...\Mods\Images`、`Models`、`Audio`… |
| 存檔 | `...\Saves\`（例如 `TS_AutoSave_*.json`） |

Workshop ID 範例：`3274191922`。若 `Mods\Workshop` 是空的，仍可從存檔載入過的桌面繼續改牌。

---

## Cube 編輯注意事項

- 主要改 `johto_cube.xlsx`；`johto_cube_ENG.xlsx` 作英文對照。  
- **檔名必須對得上**：例如 `pokedex_number` ↔ `generator_assets/pokemon/`，`move_type` ↔ `types/`，`archetype_*` ↔ `archetypes/`（archetype 鍵名維持英文，勿翻譯檔名）。  
- `move_effect` 空白時，產生器會依規則書自動帶入 archetype 說明（如 SWITCH、MULTI ALL）。  
- 有多狀態的卡，`state` 必須依序（1, 2, 3…），打亂會壞。  
- 招式效果盡量不要在 Excel 用 Alt+Enter 硬換行（原指南指出可能出錯）。  

更完整欄位說明見 `Johto War Card Generator Guide.docx`。

---

## 輔助工具（`tools/`）

| 腳本 | 用途 |
|------|------|
| `tts_download_and_crop.py` | 從 TTS 存檔／Workshop JSON 下載 CustomDeck 大圖並裁成單卡 |
| `tts_rename_cards.py` | 依存檔 Nickname 幫裁切卡重新命名 |
| `tts_crop_components.py` | 裁 Gamble 等中間插圖元件 |
| `apply_cube_translations.py` | Cube 翻譯套用輔助 |
| `translate_pdf_layout.py` | 保座標嘗試翻譯「有文字層」的 PDF（示範用） |

範例（TTS 裁切）：

```powershell
.\.venv\Scripts\python.exe tools\tts_download_and_crop.py --out tts_extract_3274191922
```

大型擷取目錄（`tts_extract_*`）已在 `.gitignore`，請勿 commit。

---

## 空白招式效果與 Archetype

規則書中 archetype 本身就有效果。Cube 裡 `move_effect` 刻意空白的招（如伏特替換／放電）不是 bug；產生器會顯示例如：

- **SWITCH**：使用此招式後，使用者可以替換退場。  
- **MULTI**：攻擊所有敵方寶可夢；僅一目標時攻擊強度 +1。  
- **MULTI ALL**：攻擊其他所有場上寶可夢；僅一目標時攻擊強度 +1。  

（完整定義見 Johto War Rulebook「MOVE ARCHETYPES」。）

---

## 常見問題

**Q: 腳本要 Cloud URL，我卡住了？**  
A: 必須先開 TTS Cloud Manager 上傳 `decks` 大圖，再把連結貼回終端機。沒有 URL 就無法產可用的 Deck Object。

**Q: 匯入後牌面還是英文／舊圖？**  
A: 確認上傳的是新產的 deck 圖、JSON 有換新 URL，且桌上物件已換成新 Saved Object（舊物件仍指向舊 Cloud 圖）。

**Q: Workshop 資料夾是空的？**  
A: 先訂閱並在 TTS 載入一次模組；或直接使用 `Saves` 裡已載過的存檔繼續製作。

**Q: 可以只更新某幾種牌嗎？**  
A: 可以，只跑對應的 `main_*.py`，只上傳該類 decks，再只匯入該類 JSON。

---

## 授權與使用

- 原版 Johto War Campaign 內容權利屬原作者／Workshop 發布者。  
- 中文翻譯由 **盤龍** 提供；使用中文版時請保留署名。  
- Pokémon 等相關商標屬其權利人所有；本倉庫僅為粉絲非官方資源。  

---

## 快速檢查清單

- [ ] 安裝 Python／venv 與 `requirements.txt`  
- [ ] 確認 `johto_cube.xlsx` 與資產齊全  
- [ ] 執行需要的 `main_*.py`  
- [ ] Cloud Manager 上傳 decks 大圖並貼回 URL  
- [ ] Deck Object JSON → Saved Objects → 匯入 TTS  
- [ ] 存檔；若要公開再 Workshop Upload，並註明翻譯：**盤龍**
