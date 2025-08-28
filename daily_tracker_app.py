import toml
import os
from datetime import datetime, timedelta
import streamlit as st

# File to store the data
DATA_FILE = "daily_tracker.toml"

def load_data():
    """Load existing data from the TOML file or initialize if not present."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return toml.load(f)
        except Exception as e:
            st.error(f"Error loading TOML file: {e}")
            return {'config': {'habits': []}}
    return {'config': {'habits': []}}

def save_data(data):
    """Save the data to the TOML file."""
    try:
        with open(DATA_FILE, 'w') as f:
            toml.dump(data, f)
    except Exception as e:
        st.error(f"Error saving TOML file: {e}")

def get_date_key(date_obj):
    """Get date as key in YYYY-MM-DD format."""
    return date_obj.strftime("%Y-%m-%d")

def parse_date_input(date_str):
    """Parse date string to datetime object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def main():
    """Main Streamlit app function."""
    st.set_page_config(page_title="Daily/Weekly Planner & Tracker", layout="wide")
    st.title("Daily/Weekly Planner and Tracker")
    st.sidebar.title("Menu")

    # Load data into session state
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    # Sidebar menu
    menu = st.sidebar.selectbox("Choose an Option", [
        "Daily Tracking",
        "Weekly Planning",
        "Adjust Future Plans",
        "View Trends",
        "Manage Habits",
        "View Summary for a Date",
        "View Week Summary"
    ])

    # Daily Tracking
    if menu == "Daily Tracking":
        today = get_date_key(datetime.now())
        if today not in st.session_state.data:
            st.session_state.data[today] = {}

        st.header(f"Daily Tracking for {today}")

        # Habits
        st.subheader("Habits")
        habits = []
        for habit in st.session_state.data['config'].get('habits', []):
            completed = st.checkbox(f"{habit}", key=f"habit_{habit}_{today}")
            habits.append({"name": habit, "completed": completed})

        extra_habit = st.text_input("Extra Habit (optional)", key=f"extra_habit_input_{today}")
        extra_habit_completed = st.checkbox("Completed?", key=f"extra_habit_completed_{today}")
        if extra_habit.strip():
            habits.append({"name": extra_habit, "completed": extra_habit_completed})

        # Tasks
        st.subheader("Tasks (Planned and New)")
        tasks = st.session_state.data[today].get('planned_tasks', [])
        task_status = {}
        if tasks:
            st.write("Planned Tasks:")
            for i, task in enumerate(tasks):
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"{i+1}. {task}")
                status = col2.selectbox("Status", ["completed", "pending", "in-progress"], key=f"task_{i}_{today}")
                task_status[task] = status
                if col3.button("Remove", key=f"remove_task_{i}_{today}"):
                    tasks.remove(task)
                    st.session_state.data[today]['planned_tasks'] = tasks
                    st.experimental_rerun()

        new_task = st.text_input("New Task", key=f"new_task_input_{today}")
        new_task_status = st.selectbox("Status", ["completed", "pending", "in-progress"], key=f"new_task_status_{today}")
        if new_task.strip():
            task_status[new_task] = new_task_status

        # Goals
        st.subheader("Goals (Planned and New)")
        goals = st.session_state.data[today].get('planned_goals', [])
        goal_progress = {}
        if goals:
            st.write("Planned Goals:")
            for i, goal in enumerate(goals):
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"{i+1}. {goal}")
                progress = col2.text_input("Progress", key=f"goal_{i}_{today}")
                goal_progress[goal] = progress
                if col3.button("Remove", key=f"remove_goal_{i}_{today}"):
                    goals.remove(goal)
                    st.session_state.data[today]['planned_goals'] = goals
                    st.experimental_rerun()

        new_goal = st.text_input("New Goal", key=f"new_goal_input_{today}")
        new_goal_progress = st.text_input("Progress", key=f"new_goal_progress_{today}")
        if new_goal.strip():
            goal_progress[new_goal] = new_goal_progress

        # Next Day Plan
        st.subheader("Plan Tasks for Tomorrow")
        next_date = datetime.now() + timedelta(days=1)
        next_key = get_date_key(next_date)
        next_tasks = st.text_area("Tasks (one per line)", key=f"next_tasks_{today}")

        if st.button("Save Daily Tracking"):
            st.session_state.data[today]['habits'] = habits
            st.session_state.data[today]['tasks'] = [{"name": t, "status": s} for t, s in task_status.items()]
            st.session_state.data[today]['goals'] = [{"name": g, "progress": p} for g, p in goal_progress.items()]
            if next_key not in st.session_state.data:
                st.session_state.data[next_key] = {}
            st.session_state.data[next_key]['planned_tasks'] = [t.strip() for t in next_tasks.split("\n") if t.strip()]
            st.session_state.data[today].pop('planned_tasks', None)
            st.session_state.data[today].pop('planned_goals', None)
            save_data(st.session_state.data)
            st.success("Daily tracking saved!")

    # Weekly Planning
    elif menu == "Weekly Planning":
        st.header("Weekly Planning")
        start_date = st.text_input("Week Start Date (YYYY-MM-DD, e.g., 2025-08-25)", key="weekly_start_date")
        if start_date:
            start = parse_date_input(start_date)
            if not start:
                st.error("Invalid date format.")
            else:
                for i in range(7):
                    day_date = start + timedelta(days=i)
                    day_key = get_date_key(day_date)
                    if day_key not in st.session_state.data:
                        st.session_state.data[day_key] = {}
                    st.subheader(f"Day {i+1}: {day_key}")
                    tasks = st.text_area(f"Tasks for {day_key} (one per line)", key=f"tasks_{day_key}")
                    goals = st.text_area(f"Goals for {day_key} (one per line)", key=f"goals_{day_key}")
                    st.session_state.data[day_key]['planned_tasks'] = [t.strip() for t in tasks.split("\n") if t.strip()]
                    st.session_state.data[day_key]['planned_goals'] = [g.strip() for g in goals.split("\n") if g.strip()]
                if st.button("Save Weekly Plan"):
                    save_data(st.session_state.data)
                    st.success("Weekly plan saved!")

    # Adjust Future Plans
    elif menu == "Adjust Future Plans":
        st.header("Adjust Future Plans")
        date_str = st.text_input("Date (YYYY-MM-DD)", key="adjust_date")
        if date_str:
            date_obj = parse_date_input(date_str)
            if not date_obj or date_obj <= datetime.now():
                st.error("Must be a future date.")
            else:
                date_key = get_date_key(date_obj)
                if date_key not in st.session_state.data:
                    st.session_state.data[date_key] = {}
                st.subheader(f"Adjusting Plans for {date_key}")
                tasks = st.text_area("Tasks (one per line)", "\n".join(st.session_state.data[date_key].get('planned_tasks', [])), key=f"adjust_tasks_{date_key}")
                goals = st.text_area("Goals (one per line)", "\n".join(st.session_state.data[date_key].get('planned_goals', [])), key=f"adjust_goals_{date_key}")
                if st.button("Save Adjustments"):
                    st.session_state.data[date_key]['planned_tasks'] = [t.strip() for t in tasks.split("\n") if t.strip()]
                    st.session_state.data[date_key]['planned_goals'] = [g.strip() for g in goals.split("\n") if g.strip()]
                    save_data(st.session_state.data)
                    st.success("Plans adjusted!")

    # View Trends
    elif menu == "View Trends":
        st.header("Trends and Consistency")
        dates = sorted([d for d in st.session_state.data if d != 'config' and datetime.strptime(d, "%Y-%m-%d") < datetime.now()])
        if not dates:
            st.write("No past data to show trends.")
        else:
            # Habits
            habit_completions = {}
            all_habits = set()
            for d in dates:
                for h in st.session_state.data[d].get('habits', []):
                    name_lower = h['name'].lower()
                    all_habits.add(name_lower)
                    if name_lower not in habit_completions:
                        habit_completions[name_lower] = {}
                    habit_completions[name_lower][d] = h['completed']

            st.subheader("Habits Trends (All Time)")
            for habit in sorted(all_habits):
                comp_dict = habit_completions.get(habit, {})
                tracked_days = [comp_dict.get(d, None) for d in dates]
                completed_count = sum(1 for c in tracked_days if c is True)
                tracked_count = sum(1 for c in tracked_days if c is not None)
                rate = (completed_count / tracked_count * 100) if tracked_count else 0
                streak = 0
                for d in reversed(dates):
                    c = comp_dict.get(d, None)
                    if c is True:
                        streak += 1
                    else:
                        break
                st.write(f"- {habit.capitalize()}: Completion rate {rate:.1f}%, Current streak: {streak} days")

            # Overall
            daily_habit_rates = []
            for d in dates:
                habits = st.session_state.data[d].get('habits', [])
                if habits:
                    rate = sum(1 for h in habits if h['completed']) / len(habits) * 100
                    daily_habit_rates.append(rate)
            avg_habit = sum(daily_habit_rates) / len(daily_habit_rates) if daily_habit_rates else 0

            daily_task_rates = []
            for d in dates:
                tasks = st.session_state.data[d].get('tasks', [])
                if tasks:
                    completed = sum(1 for t in tasks if t['status'] == 'completed')
                    rate = completed / len(tasks) * 100
                    daily_task_rates.append(rate)
            avg_task = sum(daily_task_rates) / len(daily_task_rates) if daily_task_rates else 0

            discipline = (avg_habit + avg_task) / 2 if avg_habit or avg_task else 0

            st.subheader("Overall Trends (All Time)")
            st.write(f"- Average daily habit completion: {avg_habit:.1f}%")
            st.write(f"- Average daily task completion: {avg_task:.1f}%")
            st.write(f"- Discipline score: {discipline:.1f}% (average of habit and task completions)")

            # Goals
            goal_progress = {}
            all_goals = set()
            for d in dates:
                for g in st.session_state.data[d].get('goals', []):
                    name_lower = g['name'].lower()
                    all_goals.add(name_lower)
                    if name_lower not in goal_progress:
                        goal_progress[name_lower] = []
                    goal_progress[name_lower].append((d, g['progress']))

            st.subheader("Goals Trends (Recent Progress)")
            for goal in sorted(all_goals):
                st.write(f"- {goal.capitalize()}:")
                recent = sorted(goal_progress[goal], key=lambda x: x[0], reverse=True)[:5]
                for date, prog in recent:
                    st.write(f"  {date}: {prog}")

    # Manage Habits
    elif menu == "Manage Habits":
        st.header("Manage Habits")
        st.write("Current habits: " + ", ".join(st.session_state.data['config']['habits']) if st.session_state.data['config']['habits'] else "None")
        new_habit = st.text_input("New Habit", key="new_habit")
        if st.button("Add Habit"):
            if new_habit and new_habit not in st.session_state.data['config']['habits']:
                st.session_state.data['config']['habits'].append(new_habit)
                save_data(st.session_state.data)
                st.success("Habit added!")

        remove_habit = st.text_input("Remove Habit", key="remove_habit")
        if st.button("Remove Habit"):
            if remove_habit in st.session_state.data['config']['habits']:
                st.session_state.data['config']['habits'].remove(remove_habit)
                save_data(st.session_state.data)
                st.success("Habit removed!")

    # View Summary for a Date
    elif menu == "View Summary for a Date":
        st.header("View Summary for Date")
        date_str = st.text_input("Date (YYYY-MM-DD)", key="summary_date")
        if date_str:
            date_obj = parse_date_input(date_str)
            if not date_obj:
                st.error("Invalid date format.")
            else:
                date_key = get_date_key(date_obj)
                now = datetime.now()
                is_future = date_obj > now
                is_today = date_key == get_date_key(now)

                st.subheader(f"Summary for {date_key}")
                if date_key in st.session_state.data:
                    entry = st.session_state.data[date_key]
                    st.write("**Habits:**")
                    if 'habits' in entry:
                        for habit in entry['habits']:
                            status = "Completed" if habit['completed'] else "Not Completed"
                            st.write(f"- {habit['name']}: {status}")
                    else:
                        st.write(f"Not tracked yet. Persistent habits: {', '.join(st.session_state.data['config']['habits']) if st.session_state.data['config']['habits'] else 'None'}")

                    st.write("**Actions/Tasks:**")
                    if 'tasks' in entry:
                        for task in entry['tasks']:
                            st.write(f"- {task['name']}: {task['status'].capitalize()}")
                    elif 'planned_tasks' in entry:
                        st.write("Planned tasks (not yet tracked):")
                        for task in entry['planned_tasks']:
                            st.write(f"- {task}")
                    else:
                        st.write("No tasks planned or tracked.")

                    st.write("**Goals Progress:**")
                    if 'goals' in entry:
                        for goal in entry['goals']:
                            st.write(f"- {goal['name']}: {goal['progress']}")
                    elif 'planned_goals' in entry:
                        st.write("Planned goals (not yet tracked):")
                        for goal in entry['planned_goals']:
                            st.write(f"- {goal}")
                    else:
                        st.write("No goals planned or tracked.")

                    if is_future or is_today:
                        st.write("Note: Use Daily Tracking to mark completions if today, or Adjust Future Plans for edits.")
                else:
                    st.write(f"No data or plans for {date_key}.")

    # View Week Summary
    elif menu == "View Week Summary":
        st.header("View Week Summary")
        start_date = st.text_input("Week Start Date (YYYY-MM-DD, e.g., 2025-08-25)", key="week_summary_date")
        if start_date:
            start = parse_date_input(start_date)
            if not start:
                st.error("Invalid date format.")
            else:
                for i in range(7):
                    day_date = start + timedelta(days=i)
                    day_key = get_date_key(day_date)
                    st.subheader(f"Summary for {day_key}")
                    if day_key in st.session_state.data:
                        entry = st.session_state.data[day_key]
                        st.write("**Habits:**")
                        if 'habits' in entry:
                            for habit in entry['habits']:
                                status = "Completed" if habit['completed'] else "Not Completed"
                                st.write(f"- {habit['name']}: {status}")
                        else:
                            st.write(f"Not tracked yet. Persistent habits: {', '.join(st.session_state.data['config']['habits']) if st.session_state.data['config']['habits'] else 'None'}")

                        st.write("**Actions/Tasks:**")
                        if 'tasks' in entry:
                            for task in entry['tasks']:
                                st.write(f"- {task['name']}: {task['status'].capitalize()}")
                        elif 'planned_tasks' in entry:
                            st.write("Planned tasks (not yet tracked):")
                            for task in entry['planned_tasks']:
                                st.write(f"- {task}")
                        else:
                            st.write("No tasks planned or tracked.")

                        st.write("**Goals Progress:**")
                        if 'goals' in entry:
                            for goal in entry['goals']:
                                st.write(f"- {goal['name']}: {goal['progress']}")
                        elif 'planned_goals' in entry:
                            st.write("Planned goals (not yet tracked):")
                            for goal in entry['planned_goals']:
                                st.write(f"- {goal}")
                        else:
                            st.write("No goals planned or tracked.")
                    else:
                        st.write(f"No data or plans for {day_key}.")

if __name__ == "__main__":
    main()