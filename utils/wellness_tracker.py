# utils/wellness_tracker.py
import streamlit as st  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime
import pytz # type: ignore
from utils.database import MongoDB

class WellnessTracker:
    def __init__(self):
        self.db = MongoDB()
        self.local_tz = pytz.timezone("Asia/Kolkata")  # Set your local timezone

    def render_dashboard(self):
        st.subheader("Wellness Tracking Dashboard")

        tab1, tab2, tab3 = st.tabs(["Daily Log", "Progress", "Goals"])

        with tab1:
            self.render_daily_log()

        with tab2:
            self.render_progress_charts()

        with tab3:
            self.render_goals_section()

    def render_daily_log(self):
        st.subheader("Daily Health Log")

        col1, col2 = st.columns(2)

        with col1:
            mood = st.select_slider(
                "How are you feeling today?",
                options=["😔", "😐", "🙂", "😊", "🤗"]
            )

            sleep_hours = st.number_input(
                "Hours of sleep last night",
                min_value=0,
                max_value=24,
                value=7
            )

        with col2:
            water_glasses = st.number_input(
                "Glasses of water today",
                min_value=0,
                max_value=20,
                value=0
            )

            exercise_minutes = st.number_input(
                "Minutes of exercise",
                min_value=0,
                max_value=300,
                value=0
            )

        if st.button("Save Daily Log"):
            timestamp = datetime.now(self.local_tz).isoformat()
            log_data = {
                "timestamp": timestamp,
                "mood": mood,
                "sleep_hours": sleep_hours,
                "water_glasses": water_glasses,
                "exercise_minutes": exercise_minutes
            }

            if "user" in st.session_state and st.session_state.user:
                user_id = st.session_state.user.get('_id', None)

                if not user_id:
                    st.error("⚠️ User ID not found. Please log out and log in again.")
                    return

                result = self.db.save_wellness_data(str(user_id), log_data)
                if result:
                    st.success("✅ Daily log saved successfully!")
                else:
                    st.error("❌ Failed to save daily log.")
            else:
                st.error("⚠️ Please log in to save your daily log.")

    def render_progress_charts(self):
        if "user" not in st.session_state or not st.session_state.user:
            st.warning("⚠️ Please log in to view your progress.")
            return

        user_id = st.session_state.user.get('_id', None)
        if not user_id:
            st.error("⚠️ User ID not found. Please log out and log in again.")
            return

        data = self.db.get_user_wellness_data(str(user_id))

        if not data:
            st.info("ℹ️ No wellness data available yet. Start logging daily to see your progress!")
            return

        if st.button("Reset Data"):
            deleted = self.db.delete_wellness_data(str(user_id))
            if deleted:
                st.warning("⚠️ All wellness data has been reset. Start fresh!")

                if "wellness_data" in st.session_state:
                    del st.session_state["wellness_data"]
                st.rerun()
            else:
                st.error("❌ Failed to reset wellness data.")

        daily_logs = [entry for entry in data if "mood" in entry]
        if not daily_logs:
            st.info("ℹ️ No daily log entries found.")
            return

        df = pd.DataFrame(daily_logs)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            if df["timestamp"].dt.tz is None:
                df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")

            df["timestamp"] = df["timestamp"].dt.tz_convert(self.local_tz)

        st.subheader("📊 Sleep Pattern Over Time")
        fig_sleep = px.line(df, x="timestamp", y="sleep_hours", title="Sleep Pattern Over Time")
        st.plotly_chart(fig_sleep)

        st.subheader("🏋️ Exercise Duration Over Time")
        fig_exercise = px.bar(df, x="timestamp", y="exercise_minutes", title="Exercise Minutes Over Time")
        st.plotly_chart(fig_exercise)

        st.subheader("💧 Daily Water Consumption Trend")
        fig_water = px.line(df, x="timestamp", y="water_glasses", title="Water Intake Over Time")
        st.plotly_chart(fig_water)

        # Extra: Display summary statistics
        st.subheader("Summary Statistics")
        st.write(f"Average Sleep Hours: {df['sleep_hours'].mean():.2f}")
        st.write(f"Average Exercise Minutes: {df['exercise_minutes'].mean():.2f}")
        st.write(f"Average Daily Water Intake: {df['water_glasses'].mean():.2f}")

    def render_goals_section(self):
        st.subheader("🎯 Wellness Goals")

        col1, col2 = st.columns(2)

        with col1:
            sleep_goal = st.number_input("Daily sleep goal (hours)", min_value=1, max_value=12, value=8)
            water_goal = st.number_input("Daily water intake goal (glasses)", min_value=1, max_value=20, value=8)

        with col2:
            exercise_goal = st.number_input("Daily exercise goal (minutes)", min_value=1, max_value=300, value=30)

        if st.button("Save Goals"):
            if "user" in st.session_state and st.session_state.user:
                user_id = st.session_state.user.get('_id', None)

                if not user_id:
                    st.error("⚠️ User ID not found. Please log out and log in again.")
                    return

                goals_data = {
                    "sleep_goal": sleep_goal,
                    "water_goal": water_goal,
                    "exercise_goal": exercise_goal,
                    "date_set": datetime.now(self.local_tz).isoformat()
                }
                result = self.db.save_wellness_data(str(user_id), {"goals": goals_data})
                if result:
                    st.success("✅ Goals updated successfully!")
                else:
                    st.error("❌ Failed to update goals.")
            else:
                st.error("⚠️ Please log in to set your wellness goals.")
