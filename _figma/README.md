# 設計稿本機快取

從 Figma REST API 抓下來的節點樹。**查設計稿數值先用這裡，不要重打 API。**

| 檔案 | 內容 |
|---|---|
| `node_633_963.json` | DESKTOP FINAL　1440×10274 |
| `node_633_1290.json` | MOBILE FINAL　402×7493 |
| `node_653_916.json` | Typography |
| `node_535_1382.json` | About 輪播的元件集（535:1831，五個變體）|

## 怎麼查

```bash
python3 _figma/audit.py 633:1028 4     # 印出某節點的樹：尺寸、autolayout、字體、填色
python3 _figma/figma.py find 極致養膚    # 依名稱或文字搜尋節點
python3 _figma/figma.py spec 633:1036  # 單一節點的完整屬性 JSON
```

`audit.py` 的輸出格式：

```
633:1030 FRAME 極致養膚 1280.0x839.0 [V gap=42 pad=0/110/0/110] fill=#FFFFFF@1
                                      └ autolayout：方向、間距、四邊 padding
```

## 重新抓取

```bash
curl -s -H "X-Figma-Token: $(cat ~/.figma_token)" \
  "https://api.figma.com/v1/files/1CJ813QNSVtd6K79XMXzgH/nodes?ids=633:963" \
  > _figma/node_633_963.json
```

- token 在 `~/.figma_token`（權限 600，repo 外，不會被 commit）
- fileKey `1CJ813QNSVtd6K79XMXzgH`（蒔恩美學 Copy，有完整編輯權的那份）
- **不要用 Figma MCP**：大節點會 SSE 截斷，而且 Starter 方案有呼叫上限
- `/v1/me` 會回 403（token 只有 file content 權限），用檔案端點測連線

## 匯出圖片

```bash
# 節點算圖（含裁切與壓暗等效果）
curl -s -G -H "X-Figma-Token: $(cat ~/.figma_token)" \
  --data-urlencode "ids=I633:1036;212:216" --data "format=png&scale=2" \
  "https://api.figma.com/v1/images/1CJ813QNSVtd6K79XMXzgH"

# 原始上傳檔（不含效果）
.../v1/files/<key>/images     →  imageRef 對照表
```

匯出節點會**連陰影外擴一起算進去**。本專案卡片陰影是 `6/4/16`，
模糊半徑外擴 32，所以 630×1142 的節點會匯出成 694×1206，
裁 `(26, 28, 656, 1170)` 才是卡片本體。

## 蘊膚體驗（新檔，2026-10-25 起）

| 檔案 | 內容 |
|---|---|
| `cult_desktop.json` | 藴膚體驗 桌機 1440×9721（節點 `987:1967`）|
| `cult_mobile.json`  | 藴膚體驗 mobile 425×10255（節點 `1212:1082`）|

- fileKey **`tDBBudTtmnMlCAVrMSA2f3`**（舊的 `uqWZJrgq6h8xdkerHJNssf` 已搬走，Page 3 為空）
- 兩個 frame 都在 Page `16:4` 底下

**`/v1/files/{key}/nodes` 端點被限流到 10/29 18:13**（retry-after 370741 秒）。
改用 `/v1/files/{key}?depth=N` 取整份文件再自己找節點——那是另一個額度，目前可用：

```bash
curl -s -H "X-Figma-Token: $(cat ~/.figma_token)" \
  "https://api.figma.com/v1/files/tDBBudTtmnMlCAVrMSA2f3?depth=14" -o /tmp/d14.json
```

照片用 `/v1/files/{key}/images` 取 imageRef 對照表（712 張），同樣可用。
