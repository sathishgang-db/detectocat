#!/usr/bin/env python3
import os
import json
import requests
import base64
from dotenv import load_dotenv
from nicegui import ui
from nicegui.events import UploadEventArguments

load_dotenv()


os.environ["DATABRICKS_HOST"] = "https://adb-984752964297111.11.azuredatabricks.net"
os.environ["DATABRICKS_TOKEN"] = os.environ.get("DBSQL_TOKEN")


def score_model(payload:dict)-> requests.Response:
    """
    Use the deployed model to score and fetch responses.

    Args:
        payload (dict): The input payload to be sent to the model.

    Returns:
        requests.Response: The response object containing the result of the scoring.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.
    """
    url = "https://adb-984752964297111.11.azuredatabricks.net/serving-endpoints/llava-7b-v15-sg/invocations"
    headers = {
        "Authorization": f'Bearer {os.environ.get("DBSQL_TOKEN")}',
        "Content-Type": "application/json",
    }
    json_payload = json.dumps(payload)
    response = requests.request(
        method="POST", headers=headers, url=url, data=json_payload, timeout=90.0
    )
    print(response.text)
    return response


async def send_to_bricks(e: UploadEventArguments)-> None:
    """
    Sends the uploaded image and user prompt to the bricks for processing.

    Args:
        e (UploadEventArguments): The event arguments containing the uploaded content.

    Returns:
        None
    """
    enc_image = base64.b64encode(e.content.read()).decode("ascii")
    prompt = usr_prompt.value
    print(f"INFO:User prompt value:{prompt}")
    payload = {
        "dataframe_split": {
            "columns": ["prompt", "image"],
            "data": [
                [
                    f"<image>\nUSER:{prompt}\nASSISTANT:",
                    enc_image,
                ]
            ],
        }
    }
    response = score_model(payload)
    upload._handle_text_change(text=response.json()["predictions"]["candidates"][0].split("ASSISTANT:")[1])

def reset_text():
    upload._handle_text_change(text="")
    print(f"INFO:Upload text has been cleared. New value:{upload.text}")
    usr_prompt.value = ""
    print(f"INFO:User prompt value has been cleared. New value:{usr_prompt.value}")

with ui.column().style("gap:5em"):
    with ui.row():
        dark = ui.dark_mode()
        ui.button("", on_click=dark.enable, icon="dark_mode")
        ui.button("", on_click=dark.disable, icon="light_mode")
    with ui.column():
        cat_says = ui.chat_message(
            "Hello! I am DetectoCat, a friendly AI detective cat powered by Databricks. I am here to help you with your questions and to provide you with information about the images you upload!",
            name="DetectoCat",
            avatar="https://robohash.org/BWZ.png?set=set4",
        ).style("width: 60em")
        usr_prompt = ui.input("prompt").style("width: 60em")
        ui.label("Upload Image to Interact with Detectocat")
        img = (
            ui.upload(on_upload=send_to_bricks, auto_upload=False)
            .style("width: 40em")
            .style("height: 60em")
        )
        upload = ui.label().style("width: 60em")
        ui.button("Reset", on_click=reset_text,color='red').style("width: 15em")
     

ui.run()

