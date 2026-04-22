import streamlit as st
import requests
import matplotlib.pyplot as plt
from player_store import save_player_data, get_player_history

st.title("🏏 Bowling Analysis System")

# ---------------------------
# PLAYER INPUT
# ---------------------------
player_name = st.text_input("Enter Player Name")

uploaded_file = st.file_uploader("Upload Bowling Video", type=["mp4", "avi", "mov"])

if st.button("Analyze Bowling Action"):

    if uploaded_file is not None and player_name != "":
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.read())

        st.info("Processing... Please wait")

        try:
            # CALL FASTAPI BACKEND
            files = {"file": open("temp_video.mp4", "rb")}
            response = requests.post("http://127.0.0.1:8000/analyze", files=files)

            result = response.json()

            st.success("Analysis Complete")

            # ---------------------------
            # SHOW RESULTS
            # ---------------------------
            st.subheader("📊 Results")
            st.json(result)

            # ---------------------------
            # SAVE PLAYER DATA
            # ---------------------------
            save_player_data(player_name, result)

        except Exception as e:
            st.error(f"Connection error: {e}")

# ---------------------------
# PLAYER HISTORY
# ---------------------------
st.header("📁 Player History")

if player_name != "":
    history = get_player_history(player_name)

    if len(history) > 0:

        arm_angles = []
        knee_angles = []

        for session in history:
            arm_angles.append(session.get("arm_angle", 0))
            knee_angles.append(session.get("knee_angle", 0))

        # ---------------------------
        # GRAPH
        # ---------------------------
        st.subheader("📈 Performance Trends")

        fig, ax = plt.subplots()

        ax.plot(arm_angles, marker='o', label="Arm Angle")
        ax.plot(knee_angles, marker='o', label="Knee Angle")

        ax.set_xlabel("Session")
        ax.set_ylabel("Angle")
        ax.set_title("Performance Trend")

        ax.legend()

        st.pyplot(fig)

    else:
        st.warning("No data found for this player")