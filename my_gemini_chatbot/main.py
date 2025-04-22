import vertexai
from nicegui import ui, app
from jinja2 import Environment, PackageLoader, select_autoescape
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

credentials=service_account.Credentials.from_service_account_file("learn-304807-11f1d329d997.json")

vertexai.init(project="learn-304807", location="us-central1", credentials=credentials)

env = Environment(
    loader=PackageLoader("my_gemini_chatbot"),
    autoescape=select_autoescape()
)

model = GenerativeModel("gemini")
# ui.label('Hello NiceGUI!')

def get_chat_response(chat,prompt):
    text_response=[]
    responses=chat.send_message(prompt,stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return ''.join(text_response)

def get_personality_file(value):
    match value:
        case "Default":
            return "default.jinja"
        case "Santa Claus":
            return "santaclaus.jinja"
        case "Dad Jokes":
            return "dadjokes.jinja"
        case _:
            return "default.jinja"

def send():
    user_prompt=app.storage.client.get("prompt")
    personality=app.storage.client.get("personality")
    
    personality_template=env.get_template(get_personality_file(personality))
    prompt_template=env.get_template("prompt.jinja")

    # print(personality_template)
    prompt = prompt_template.render(
        prompt=user_prompt,
        personality=personality_template.render()
    )

    ui.notify(
        "Sending to Gemini...",
        type="info"
    )

    chat=model.start_chat()
    response=get_chat_response(chat,prompt)
    ui.notify("Received Respinse...",type="info")

    app.storage.client["response"]=response

@ui.page('/')
def index():
    with ui.grid(columns=16).classes("w-3/4 place-self-center gap-4"):
        ui.markdown("# 🚀My Gemini Chatbot🚀").classes("col-span-full")
        ui.input(label="Prompt").bind_value(app.storage.client,"prompt").classes("col-span-10")
        ui.select(
            options=["Default","Santa Claus","Dad Jokes"],
            value="Default",
            label="Personality"
        ).bind_value(app.storage.client,"personality").classes("col-span-6")
        ui.button("Send to Gemini", on_click=send).classes("col-span-8")
        dark = ui.dark_mode()
        ui.button("Light UI",on_click=dark.disable).classes("col-span-4")
        ui.button("Dark UI",on_click=dark.enable).classes("col-span-4")
        

        with ui.card().classes("col-span-full"):
            ui.markdown("## Gemini Response")
            ui.separator()
            ui.label().bind_text(app.storage.client,"response")

ui.run()