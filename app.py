import streamlit as st
import tempfile
from analyzer import analyze_video
from player_store import save_session, get_players
import matplotlib.pyplot as plt

st.set_page_config(page_title="Cricket AI Analyzer", layout="wide")

st.title("🏏 Cricket Bowling Performance System")

# -------- LOAD PLAYERS --------
players = get_players()
player_names = [p.get("name", "") for p in players if p.get("name")]

selected_player = st.selectbox("Select Player", ["New Player"] + player_names)

if selected_player == "New Player":
    player = st.text_input("Player Name")
    age = st.number_input("Age", 10, 50)
    height = st.number_input("Height (cm)")
    weight = st.number_input("Weight (kg)")
else:
    player = selected_player
    st.write(f"Analyzing Player: {player}")
    age, height, weight = 0, 0, 0

camera = st.selectbox("Camera Angle", ["Side View", "Rear View"])
video = st.file_uploader("Upload Bowling Video", type=["mp4"])

# -------- ANALYSIS --------
if video:
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(video.read())
    video_path = temp.name

    st.video(video)

    if st.button("Analyze Bowling"):

        if not player or player.strip() == "":
            st.error("Enter player name")
            st.stop()

        result = analyze_video(video_path, camera)

        if not result or "error" in result:
            st.error(result.get("error", "Analysis failed"))
        else:
            save_session(
                {
                    "name": player,
                    "age": age,
                    "height": height,
                    "weight": weight
                },
                result
            )

            # =========================
            # 🎯 PERFORMANCE SCORE (FIXED)
            # =========================
            arm = result.get("arm_angle", 0)
            knee = result.get("knee_angle", 0)

            score = 0

            # Arm scoring
            if arm >= 185:
                score += 3
            elif arm >= 170:
                score += 2
            else:
                score += 1

            # Knee scoring
            if knee >= 165:
                score += 3
            elif knee >= 145:
                score += 2
            else:
                score += 1

            # Risk scoring
            if not result.get("knee_risk"):
                score += 2
            if not result.get("shoulder_risk"):
                score += 2

            score = min(round(score, 1), 10)

            # =========================
            # 🚨 ISSUE DETECTION (IMPROVED)
            # =========================
            issues = []

            if knee < 145:
                issues.append(("High", "Front knee collapsing"))

            if arm < 170:
                issues.append(("Medium", "Low arm release"))

            if result.get("consistency") == "Inconsistent action":
                issues.append(("Medium", "Inconsistent bowling action"))

            # Sort by priority
            issues_sorted = sorted(issues, key=lambda x: x[0] == "Medium")

            main_issue = issues_sorted[0][1] if issues_sorted else "No major issue"

            # =========================
            # 📊 REPORT OUTPUT
            # =========================
            st.header("📊 Performance Report")

            st.subheader(f"Overall Score: {score} / 10")

            st.write("### 🚨 Main Issue")
            st.write(main_issue)

            st.write("### 🎯 Priority Fix Order")
            if issues_sorted:
                for i, (_, issue) in enumerate(issues_sorted, 1):
                    st.write(f"{i}. {issue}")
            else:
                st.write("Maintain current performance")

            # =========================
            # 📉 IMPACT ANALYSIS
            # =========================
            st.write("### 📉 Performance Impact")

            if knee < 145:
                st.write("• Reduced pace due to poor energy transfer")
                st.write("• Loss of stability at crease")

            if arm < 170:
                st.write("• Reduced bounce and seam control")

            if result.get("consistency") == "Inconsistent action":
                st.write("• Line and length inconsistency")

            # =========================
            # ⚙ TECHNICAL FEEDBACK
            # =========================
            st.write("### ⚙ Technical Analysis")

            st.write("**Arm Mechanics:**")
            st.write(result.get("arm_feedback", "No data"))

            st.write("**Front Leg Mechanics:**")
            st.write(result.get("knee_feedback", "No data"))

            # =========================
            # 🏋 ACTION PLAN
            # =========================
            st.write("### 🏋 Action Plan")

            if knee < 145:
                st.write("• Squats – 3×10 reps")
                st.write("• Lunges – 3×8 each leg")
                st.write("• Front leg bracing drills")

            if arm < 170:
                st.write("• High-arm shadow bowling drills")
                st.write("• Alignment training")

            if result.get("consistency") == "Inconsistent action":
                st.write("• Repeatable run-up drills")
                st.write("• Target bowling sessions")

            if not issues:
                st.write("• Maintain technique")
                st.write("• Focus on match simulation")

            # =========================
            # ⚠ RISK LEVEL
            # =========================
            st.write("### ⚠ Risk Level")

            if result.get("knee_risk") or result.get("shoulder_risk"):
                st.error("Medium to High Risk")
            else:
                st.success("Low Risk")

# =========================
# 📈 GRAPH DASHBOARD
# =========================
st.header("📈 Performance Trends")

players = get_players()

for p in players:
    if p.get("name") == player:

        sessions = p.get("sessions", [])

        if len(sessions) >= 2:

            arm = [s.get("arm_angle", 0) for s in sessions if s.get("arm_angle") is not None]
            knee = [s.get("knee_angle", 0) for s in sessions if s.get("knee_angle") is not None]
            labels = [s.get("date", "") for s in sessions]

            if arm and knee:

                fig1 = plt.figure()
                plt.plot(labels[:len(arm)], arm, marker='o')
                plt.xticks(rotation=45)
                plt.title("Arm Angle Trend")
                plt.tight_layout()
                st.pyplot(fig1)

                fig2 = plt.figure()
                plt.plot(labels[:len(knee)], knee, marker='o')
                plt.xticks(rotation=45)
                plt.title("Knee Angle Trend")
                plt.tight_layout()
                st.pyplot(fig2)