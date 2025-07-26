import streamlit as st
from api_utils import get_api_response, send_feedback
from PIL import Image

# Load avatars
user_avatar = Image.open("query_logo.jpg")           # e.g. a rectangular icon with 'Y' or 'YOU'
assistant_avatar = Image.open("response_logo.jpg")  # e.g. RJ sir as AI icon

def display_chat_interface():
    # Show message history
    for message in st.session_state.messages:
        avatar = user_avatar if message["role"] == "user" else assistant_avatar
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about growing your business..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.last_query = prompt

        with st.chat_message("user", avatar=user_avatar):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)

            if response:
                st.session_state.session_id = response.get("session_id")
                answer = response["answer"]
                st.session_state.last_answer = answer
                st.session_state.messages.append({"role": "assistant", "content": answer})

                with st.chat_message("assistant", avatar=assistant_avatar):
                    st.markdown(answer)

    # Feedback form
    if "last_answer" in st.session_state:
        with st.expander("Was this response helpful?"):
            with st.form(key=f"feedback_form_{len(st.session_state.messages)}"):
                feedback = st.radio("Your Feedback", ["Good", "Bad"])
                comments = st.text_area("✍️ Help us improve by sharing your thoughts (required if you select 'Bad')", height=100)
                submit = st.form_submit_button("Submit Feedback")

                if submit:
                    if feedback == "Bad" and len(comments.strip()) < 10:
                        st.warning("⚠️ Please provide some written feedback so we can understand the issue.")
                    else:
                        full_feedback = f"{feedback}: {comments.strip()}" if comments.strip() else feedback
                        success = send_feedback(
                            session_id=st.session_state.session_id,
                            user_query=st.session_state.last_query,
                            model_response=st.session_state.last_answer,
                            feedback=full_feedback
                        )
                        if success:
                            st.success("✅ Thank you! Your feedback has been submitted.")
                        else:
                            st.error("❌ Failed to submit feedback. Please try again.")

