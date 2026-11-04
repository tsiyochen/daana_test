/**
 * 蒔恩美學診所 —— 開幕邀請卡後端
 *
 * 安裝：開那張 Google Sheet → 擴充功能 → Apps Script → 把這整份貼上去
 *       → 部署 → 新增部署作業 → 類型「網頁應用程式」
 *       → 執行身分「我」、access「任何人」→ 部署 → 複製 /exec 結尾的網址
 *
 * ⚠️ 以後改這支腳本，一定要再「部署 → 管理部署作業 → 編輯 → 版本：新版本」，
 *    否則網址上跑的還是舊版。這是 Apps Script 最常見的坑。
 *
 * 權限：這支腳本只用 getActiveSpreadsheet()，也就是它自己被貼在哪張 Sheet 就只碰那張。
 *      沒有 DriveApp、沒有 openById，程式裡沒有任何一行有能力指向別的檔案。
 *      授權視窗若出現「您的所有 Google 試算表檔案」，照「開幕邀請卡-appsscript.json」
 *      把 oauthScopes 寫死成 spreadsheets.currentonly，範圍就會縮到只剩當前這一張。
 */

const TAB  = '回覆';
const HEAD = ['時間', '出席', '人數', '署名', '留言', '上牆', '編號'];

// 欄位位置（1 起算），改欄位順序時只要改這裡
const COL = { time:1, attend:2, guests:3, name:4, message:5, wall:6, id:7 };


function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(TAB) || ss.insertSheet(TAB);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEAD);
    sh.setFrozenRows(1);
    sh.setColumnWidth(COL.message, 420);
  }
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}


/** 邀請卡送出一筆 */
function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);          // 同時有人送出時排隊，不會互相蓋掉
  } catch (err) {
    return json_({ ok: false, error: 'busy' });
  }
  try {
    const d  = JSON.parse(e.postData.contents);
    const id = String(d.id || '').slice(0, 40);
    if (!id) return json_({ ok: false, error: 'no id' });

    const sh = sheet_();
    const n  = sh.getLastRow() - 1;

    // 同一筆重送不會變成兩列 —— 邀請卡送出失敗會自動補送，沒有這段就會重複
    const seen = n > 0
      ? sh.getRange(2, COL.id, n, 1).getValues().map(r => String(r[0]))
      : [];
    if (seen.indexOf(id) === -1) {
      sh.appendRow([new Date(), d.attend || '', d.guests || '',
                    d.name || '', d.message || '', false, id]);
      sh.getRange(sh.getLastRow(), COL.wall).insertCheckboxes();
    }
    return json_({ ok: true, id: id });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}


/** 留言牆：只回傳「上牆」打勾的那幾列，而且只給署名與留言 */
function doGet() {
  try {
    const sh = sheet_();
    const n  = sh.getLastRow() - 1;
    const out = [];
    if (n > 0) {
      sh.getRange(2, COL.name, n, 3).getValues().forEach(r => {   // 署名 / 留言 / 上牆
        const name = String(r[0]).trim(), message = String(r[1]).trim();
        if (r[2] === true && message) out.push({ name: name, message: message });
      });
    }
    return json_({ ok: true, messages: out.reverse() });          // 新的在前
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}


/** 在編輯器裡直接按執行，確認權限與欄位都對 */
function 測試寫入() {
  doPost({ postData: { contents: JSON.stringify({
    id: 'test-' + Date.now(), attend: '出席', guests: '2',
    name: '測試用，可以刪掉', message: '這是一筆測試留言。'
  })}});
  Logger.log('寫好了，去「回覆」分頁看最後一列');
}
