import io
import shutil
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

# フォルダーのIDを指定
folder_id = '1cUyCmCEl865rnZXjIywa0P9OcwwNm5Ac'

# Google Drive APIの認証情報を取得
def get_credentials():
    # 認証情報の取得処理を実装
    scope = ["https://www.googleapis.com/auth/drive.file"]
    keyFile = "sa.json"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(keyFile, scopes=scope)
    return credentials

def download_csv(file_name):
    # Google Drive APIの認証情報を取得
    service = build("drive", "v3", credentials=get_credentials())

    # csvファイルを検索
    query = f"'{folder_id}' in parents and trashed = false and name='{file_name}'"
    results = service.files().list(q=query, fields='nextPageToken, '
                                                  'files(id, name)').execute()
    files = results.get('files', [])

    # ファイルが存在する場合、ダウンロードを実行
    if files:
        file_id = files[0]['id']
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {file_name} {int(status.progress() * 100)}.')

        # ダウンロードしたファイルを保存
        fh.seek(0)
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(fh, f, length=131072)

for i in range(1, 3):
    ts = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
    file_name = f"{ts}.csv"
    download_csv(file_name)
