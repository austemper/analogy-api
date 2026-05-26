import os
import base64
import tempfile
import logging
from graph_rag import run_pipeline
from graphistry_sync import update_graphistry
from state import JOBS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime


def get_credentials_path():
    creds_b64 = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if creds_b64:
        creds_data = base64.b64decode(creds_b64).decode("utf-8")
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        tmp.write(creds_data)
        tmp.close()
        return tmp.name
    return "credentials.json"


def write_to_sheet(concept, status, total, url, job_id):

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        get_credentials_path(), scope
    )

    client = gspread.authorize(creds)

    sheet = client.open("job_logs").sheet1

    sheet.append_row([
    str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    status,  
    concept,
    total,
    url,
    job_id
])

def worker(job_id, concept):

    print(f"[{job_id}] START")

    try:

        print(f"[{job_id}] run_pipeline START")
        output = run_pipeline(concept)
        print(f"[{job_id}] run_pipeline END")
        stats = output["llm_stats"]
        print(f"[{job_id}] update_graphistry START")
        url = update_graphistry()
        print(f"[{job_id}] update_graphistry END")

        # ===== job保存 =====
        JOBS[job_id] = {
            "status": "done",
            "result": output["modes"],
            "stats": output["llm_stats"],
            "graph_url": url
            }
        print(f"[{job_id}] DONE")
        
        
    except Exception as e:

        logging.exception(f"Graphistryの更新に失敗しました…: {e}")

        JOBS[job_id] = {
            "status": "error",
            "error": str(e)
        }

        # エラーも記録
        write_to_sheet(concept, "error", total, url, job_id)
        
        return
    
    


    # ===== ログ =====
    logging.info("===========パイプライン完了==========")
    logging.info(f"concept: {concept}")

    for k, v in stats.items():
        total = v["prompt_tokens"] + v["response_tokens"]
        logging.info(
            f"[{k}] calls={v['calls']} prompt={v['prompt_tokens']} response={v['response_tokens']} total={total}"
        )

    logging.info("=======================================")
    logging.info(f"GRAPH URL = {url}")

    # ===== google sheetに保存 =====
    write_to_sheet(concept, "done", total, url, job_id)
