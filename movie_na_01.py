import streamlit as st
import openai
import base64
import cv2
import tempfile
import time

# OpenAI APIキーの入力
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("OpenAI API Key")
openai.api_key = api_key


def get_frames_from_video(file):
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(file.read())

    video = cv2.VideoCapture(tfile.name)
    base64_frames = []
    
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break

        _, buffer = cv2.imencode(".jpg", frame)
        base64_frame = base64.b64encode(buffer).decode("utf-8")
        base64_frames.append(base64_frame)

    video.release()
    return base64_frames,buffer

@st.cache_data
def get_text_from_video(file):
    # ビデオからフレームを取得し、それらをbase64にエンコードする
    base64_frames, buffer = get_frames_from_video(file)

    # GPT-4 Vision APIにリクエストを送信
    PROMPT_MESSAGES = [
        {
        "role": "user",
        "content": [
            "These are frames of a video. Create a short voiceover script . Only include the narration. Please Japanese.",
            *map(lambda x: {"image": x, "resize": 768}, base64_frames[0::90]),
            ],
        },
    ]
    
    params = {
    "model": "gpt-4-vision-preview",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 500,
}
    
    response = openai.chat.completions.create(**params)
    time.sleep(0.5) 
    return response.choices[0].message.content, buffer

@st.cache_data
def get_audio_from_text(text):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input= text
    )
    return response.content

uploaded_file = st.file_uploader("Choose a video file", type="mp4")
if uploaded_file is not None:
    #client = OpenAI()
    text,buffer = get_text_from_video(uploaded_file)
    st.text(text)
    st.image(buffer.tobytes(), width=200)

    # テキストデータをtxtファイルとしてダウンロード
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="output.txt">Download Text File</a>'
    st.markdown(href, unsafe_allow_html=True)

    audio = get_audio_from_text(text)

    # 音声を再生
    audio_file = open("output.mp3", "wb")
    audio_file.write(audio)
    audio_file.close()
    audio_file = open("output.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

    # 音声をダウンロード
    b64 = base64.b64encode(audio).decode()
    href = f'<a href="data:file/mp3;base64,{b64}" download="output.mp3">Download MP3 File</a>'
    st.markdown(href, unsafe_allow_html=True)