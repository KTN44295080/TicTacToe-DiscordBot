# n目並べDiscordBot
Discord内で動作するn目並べで遊べるBot。<br>
コンピューターとの対戦と2人プレイの両方に対応。

# Requirement

### 環境
* Pythom 3.11
### 必要なパッケージ
* mojimoji
* discord.py
* py-cord

# Installation
以下のサイトでDiscordのBotを作成し、アクセストークンの取得と権限の付与を行う。<br>
https://discord.com/developers/applications?new_application=true
### アクセストークンの取得
New Applicationを押下、適当な名前を入力しCreate。<br>
左側のメニューからBotを選択し、Reset Tokenボタンを押下するとアクセストークンが表示されるのでCopyボタンを押下してコピーする。<br>
bot.pyと同じディレクトリ内に.envという名前のファイルを作成し、<br>
TOKEN = コピーしたトークン<br>
と記載して保存する。
### 権限の付与
左側メニューからBotを選択し、Privileged Gateway Intents内のPRESENCE INTENT、SERVER MEMBERS INTENT、MESSAGE CONTENT INTENTを有効化し、下部に表示されるSave Changesボタンを押下して保存する。<br>
次に左側のメニューからOAuth2→URL Generatorを選択し、SCOPES内のbotとapllications.commandsにチェックを入れた後。下に表示されるBOT PERMISSIONS内のSend Messagessにもチェックを入れる。<br>
最後にその下に表示されるURLをCopyしてアクセスすればBotを任意のサーバーに追加できる。
### 動作に必要なパッケージをインポート
ターミナル等でCloneした本リポジトリのフォルダに移動し、以下のコマンドを実行する。

```bash
pip install -r requirements.txt
```

# Usage

パッケージをインストール後、ターミナル等でCloneした本リポジトリのフォルダに移動し、以下のコマンドを実行する。

```bash
python bot.py
```