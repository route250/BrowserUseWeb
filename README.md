# BrowserUseWeb

Browser-useをFlaskベースのWebアプリケーション化しました。
自然言語でのブラウザ操作を行うサンプル実装です。

https://github.com/browser-use

また、ブラウザ画面の転送にnoVNCを同梱しています。
https://github.com/novnc

## セキュリティ注意事項

サンプル実装なので、通信の暗号化(SSL)は行っていません。
安全なネットワーク内で試用して下さい。

## 主な機能

- Browser-useによるタスク実行
  - 自然言語によるタスク指示をもとにLLMがブラウザを自動操作

- Webインターフェース
  - Browser-useとブラウザをサーバで実行するので、ユーザ(クライアント)での環境構築が不要

- マルチユーザ対応
  - 最大１０ユーザ(セッション)まで同時利用可能

## 前提条件

OS側に、以下のパッケージが必要です：

- Ubuntu 24.04
  - tigervnc-standalone-server
  - websockify
  - google-chrome

- RHEL9(Rocky9,Alma9,...)
  - tigervnc-server
  - python3-websockify
  - google-chrome

## セットアップ

1. リポジトリクローン
```bash
git clone https://github.com/route250/BrowserUseWeb.git
cd BrowserUseWeb
```

2. python仮想環境
```bash
python3.12 -m venv .venv --prompt 'Browser'
source .venv/bin/activate
.venv/bin/python -m pip install -U pip setuptools
```

3. pythonパッケージをインストール
```bash
pip install -r requirements.txt
```

4. playwriteのセットアップ

playwriteでブラウザをインストールしてください。

```
playwright install chromium
```

6. 実行権限の付与：
```bash
chmod +x app.py
```

7. 環境変数にAPIキーを設定：
```bash
export OPENAI_API_KEY="your-api-key"
```

8. ファイアウォール設定
- Ubuntu 24.04
```bash
ufw allow 5000/tcp # flaskサーバ用
ufw allow 5030:5099/tcp # websock用
```

- RHEL9(Rocky9,Alma9,...)
```bash
firewall-cmd --add-port=5000/tcp # flaskサーバ用
firewall-cmd --add-port=5030:5099/tcp # websock用
```

9. ubuntu 24.04の場合、以下の設定が必要

```bash
sudo sysctl -w kernel.apparmor_restrict_unprivileged_unconfined=0
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
```

## 使用方法

1. アプリケーション起動：
```bash
./app.py
```

2. Webブラウザでアクセス：
```
http://localhost:5000
```

3. 操作手順：
   - タスク入力欄に実行したい内容を日本語で入力
   - 「タスク実行」ボタンをクリックして処理を開始
   - 実行状況は左下のログ出力エリアに表示
   - 「タスクキャンセル」ボタンで処理を停止

4. ブラウザが起動しない時

以下のシェルスクリプトを修正すると動くかもしれません。
- buweb/scripts/start_browser.sh
- buweb/scripts/start_vnc.sh

## システム構成

- `app.py`: Flaskアプリケーションのメインファイル
  - HTTPリクエストのハンドリング
  - セッション管理
  - APIエンドポイントの提供
- `session.py`: セッション管理クラス
  - Xvncサーバーの自動起動/停止
  - websockifyによるWebSocket接続
  - Chromeブラウザの起動管理
  - セッションのクリーンアップ
- `browser_task.py`: ブラウザ自動操作
  - 自然言語によるタスク指示
  - ブラウザ操作の実行制御
  - タスク進捗の管理
- `static/index.html`: フロントエンドインターフェース
  - リアルタイムステータス表示
  - WebSocket/SSE通信
  - noVNCによるブラウザベースのVNCクライアント
- `buweb/scripts/start_vnc.sh`: VNCサーバ起動スクリプト
  - Xvncの環境設定と起動停止
- `buweb/scripts/start_browser.sh`: ブラウザ起動スクリプト
  - bwrapによる環境分離
  - ブラウザの起動と停止
  
## 技術仕様

- **バックエンド**
  - Flask: 非同期Webアプリケーションフレームワーク

- **Web自動処理**
  - Browser-use: 自然言語によるブラウザ操作

- **VNC関連**
  - Xvnc: ヘッドレスVNCサーバー
  - websockify: TCPからWebSocketへのプロキシ
  - noVNC: HTML5 VNCクライアント
  - デフォルトの解像度: 1024x1024

- **ブラウザ制御**
  - Chrome DevTools Protocol

## ライセンス

このプロジェクトはMIT Licenseの下で提供されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

また、browser-useのライセンス、noVNCのライセンスは別途参照して下さい。
https://github.com/browser-use
https://github.com/novnc


selinuxuser_execmod' boolean
