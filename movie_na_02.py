import openai
import streamlit as st
openai.api_key = 'your-api-key-here'
st.header('音声文字起こしアプリ')

upload_file = st.file_uploader('音声文字起こしするファイルを選択してください  \nAPIの上限により25MB以上のファイルは文字起こし不可です。\
                               ファイルを分割する等容量を少なくしてください', type=['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav'])
if upload_file is not None:
    st.subheader('ファイル詳細')
    file_details = {'FileName': upload_file.name, 'FileType': upload_file.type, 'FileSize': upload_file.size}
    st.write(file_details)
    file_name=upload_file.name.split('.')[0]
    if upload_file.size > 25000000:
        st.error('エラー：ファイルが25MBを超えています。APIの上限により25MB以上のファイルは文字起こし不可です。ファイルを分割する等容量を少なくしてください', icon="🚨")

if st.button('文字起こし開始',key="w_button"):
    if upload_file is None:
        st.error('エラー：ファイルが選択されていません', icon="🚨")
    else:
        with st.spinner('***音声文字起こしを実行中です...***'):
            trans= openai.Audio.transcribe("whisper-1" ,upload_file)["text"]
        st.success('***音声文字起こしを完了しました***')
        st.write(trans)
