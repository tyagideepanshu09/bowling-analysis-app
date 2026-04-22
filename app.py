import streamlit as st
import matplotlib.pyplot as plt
import uuid
import os

from analyzer import analyze_video
from player_store import save_player_data, get_player_history

st.title("🏏 Bowling Analysis System")

# ---------------------------
# INPUT
# ---------------------------
player_name = st.text_input("Enter Player Name")
uploaded_file = st.file_uploader("Upload Bowling Video", type=["mp4", "avi", "mov"])

# ---------------------------
# ANALYSIS
# ---------------------------
if st.button("Analyze Bowling Action"):

    if uploaded_file is not None and player_name != "":

        temp_filename = f"temp_{uuid.uuid4()}.mp4"

        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Processing... Please wait")

        try:
            # DIRECT ANALYSIS (NO BACKEND)
            result = analyze_video(temp_filename)

            st.success("Analysis Complete")

            # SHOW RESULT
            st.subheader("📊 Results")
            st.json(result)

            # SAVE DATA
            save_player_data(player_name, result)

            # DELETE TEMP FILE
            os.remove(temp_filename)

        except Exception as e:
            st.error(f"Error: {e}")

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