import streamlit as st
import base64
import time
import openai
from openai import OpenAI
from tempfile import NamedTemporaryFile
from streamlit_image_select import image_select
from mockup_code import mockup_1, mockup_2

# App title
st.set_page_config(page_title='🛠 Streamlit App Builder', page_icon='🛠')
st.title('🛠 Streamlit App Builder')
st.info('In this app you can **Show** (provide mock-up image) or **Tell** (provide text prompt) how you want your Streamlit app to be built.')

# Initialize OpenAI client with API key
api_key = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

tabs = st.tabs(['Show', 'Tell'])

# Show how the app should be built
with tabs[0]:
    # Upload image
    upload_img = st.toggle('Upload your own mock-up images')
    if upload_img:
        st.subheader('Upload your own mock-up image')
        image_upload = st.file_uploader('Upload an image', type=['png', 'jpg', 'jpeg'])

        # Function to encode the image
        def encode_image(image_file):
            return base64.b64encode(image_file.read()).decode('utf-8')

        if image_upload:
            st.image(image_upload, use_column_width=True)
            bytes_data = image_upload.read()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')

    # Example images
    example_img = st.toggle('Try example mock-up images')
    if example_img:
        st.subheader('Try these example mock-up images')
        img = image_select(
            label="Select a mock-up image",
            images=[
                "img/streamlit-app-mockup-1.png",
                "img/streamlit-app-mockup-2.png"
            ],
        )

    with st.expander('Expand to see prompt instructions'):
        prompt_instructions = '''You are an experienced Python developer who can build amazing Streamlit apps.
            You will be given a mock-up image of a Streamlit app for which you will convert it to a Streamlit app by generating the Python code.
            If a graph is present in the app, instead of generating random data, please try to mimic the data points shown.
            If asked to do anything other than creating a Streamlit app, politely refuse.'''
        st.markdown(prompt_instructions)

    # Start LLM process
    if not upload_img and not example_img:
        start_button = st.button('Build', key='button_image_start', disabled=True)
    else:
        start_button = st.button('Build', key='button_image_start', disabled=False)

    if any([upload_img, example_img]):

        if 'img' in locals() or 'img' in globals():
            if start_button:
                with st.spinner('Processing ...'):
                    time.sleep(1.5)

                    if img == "img/streamlit-app-mockup-1.png":
                        st.subheader("Input")
                        st.image("img/streamlit-app-mockup-1.png")
                        st.subheader("Output")
                        mockup_1()

                    if img == "img/streamlit-app-mockup-2.png":
                        st.subheader("Input")
                        st.image("img/streamlit-app-mockup-2.png")
                        st.subheader("Output")
                        mockup_2()

        elif image_upload is not None and api_key and start_button:
            with st.spinner('Processing ...'):
                messages = [
                    {
                        'role': 'user',
                        'content': prompt_instructions + f"\n![Mockup Image](data:image/jpeg;base64,{base64_image})"
                    }
                ]

                try:
                    # Response generation
                    full_response = ''
                    message_placeholder = st.empty()

                    for completion in client.chat.completions.create(
                            model='gpt-4o', messages=messages,
                            max_tokens=1280, stream=True):

                        if completion.choices[0].delta.content is not None:
                            full_response += completion.choices[0].delta.content
                            message_placeholder.markdown(full_response + '▌')

                    message_placeholder.markdown(full_response)

                    parsed_output = full_response.split('```python')[1].lstrip('\n').split('```')[0]

                    # Clear results
                    if st.button('Clear', key='button_image_clear'):
                        os.remove(tmp.name)

                except Exception as e:
                    st.error(f'An error occurred: {e}')

        else:
            if not image_upload and start_button:
                st.warning('Please upload your mock-up image.')
            if not api_key:
                st.warning('Please provide your OpenAI API key.')

# Tell how the app should be built
with tabs[1]:
    text_prompt = st.text_area(
        "Describe details on the functionalities of the Streamlit app that you want to build.",
        "",
        height=240
    )

    with st.expander('Expand to see system prompt'):
        prompt_instructions = '''You are an experienced Python developer who can build amazing Streamlit apps.
            You will be given a mock-up image of a Streamlit app for which you will convert it to a Streamlit app by generating the Python code.
            If a graph is present in the app, instead of generating random data, please try to mimic the data points shown.
            If asked to do anything other than creating a Streamlit app, politely refuse.'''
        st.markdown(prompt_instructions)

    # Start LLM process
    start_button = st.button('Build', key='button_text_start')

    if text_prompt is not None and api_key and start_button:
        with st.spinner('Processing ...'):
            messages = [
                {"role": "system", "content": "You are an experienced Python developer who can build amazing Streamlit apps."},
                {"role": "user", "content": text_prompt}
            ]
            try:
                # Response generation
                full_response = ''
                message_placeholder = st.empty()

                for completion in client.chat.completions.create(
                        model='gpt-4o', messages=messages,
                        max_tokens=1280, stream=True):

                    if completion.choices[0].delta.content is not None:
                        full_response += completion.choices[0].delta.content
                        message_placeholder.markdown(full_response + '▌')

                message_placeholder.markdown(full_response)

                parsed_output = full_response.split('```python')[1].lstrip('\n').split('```')[0]

                # Clear results
                if st.button('Clear', key='button_text_clear'):
                    os.remove(tmp.name)

            except Exception as e:
                st.error(f'An error occurred: {e}')

    else:
        if not text_prompt and start_button:
            st.warning('Please provide your text prompt.')
        if not api_key:
            st.warning('Please provide your OpenAI API key.')
