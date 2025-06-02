
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mexicano Scoring App", layout="wide")
st.title("🎾 Mexicano Format Scoring App (2 courts)")

st.markdown("""
This app automatically schedules matches for a 12-player Mexicano format 
using 2 courts. Round 1 and Round 2 are fixed; subsequent rounds are based on rankings.
""")

# Sidebar: Player list input
st.sidebar.header("Player Setup")
player_input = st.sidebar.text_area("Enter 12 player names (one per line):")
players = []
if player_input:
    players = [name.strip() for name in player_input.strip().split("\n") if name.strip()]
    if len(players) != 12:
        st.sidebar.error("Please enter exactly 12 player names.")
    else:
        st.sidebar.success("✅ 12 players added.")

# Function to get winner team from scores
def get_winner(team1, team2, score1, score2):
    if score1 > score2:
        return team1
    elif score2 > score1:
        return team2
    else:
        # In case of tie, default to team1
        return team1

if players:
    # Initialize score dict
    if 'scores' not in st.session_state:
        st.session_state.scores = {p: 0 for p in players}
    if 'round_completed' not in st.session_state:
        st.session_state.round_completed = 0

    # Round 1: fixed matches on both courts
    if st.session_state.round_completed < 1:
        st.header("🔵 Round 1 (Fixed)")
        st.write("**Court 1**: Player 1 & 2 vs Player 3 & 4")
        st.write(f"Teams: **{players[0]} & {players[1]}** vs **{players[2]} & {players[3]}**")
        c1_s1 = st.number_input("Court 1 - Team1 Score", min_value=0, max_value=4, key="r1c1_s1")
        c1_s2 = st.number_input("Court 1 - Team2 Score", min_value=0, max_value=4, key="r1c1_s2")
        st.write("**Court 2**: Player 5 & 6 vs Player 7 & 8")
        st.write(f"Teams: **{players[4]} & {players[5]}** vs **{players[6]} & {players[7]}**")
        c2_s1 = st.number_input("Court 2 - Team1 Score", min_value=0, max_value=4, key="r1c2_s1")
        c2_s2 = st.number_input("Court 2 - Team2 Score", min_value=0, max_value=4, key="r1c2_s2")

        if st.button("Submit Round 1 Scores"):
            # Update scores
            for p in [players[0], players[1]]:
                st.session_state.scores[p] += c1_s1
            for p in [players[2], players[3]]:
                st.session_state.scores[p] += c1_s2
            for p in [players[4], players[5]]:
                st.session_state.scores[p] += c2_s1
            for p in [players[6], players[7]]:
                st.session_state.scores[p] += c2_s2
            # Store winners for Round 2
            st.session_state.winner1 = get_winner(
                (players[0], players[1]), (players[2], players[3]), c1_s1, c1_s2
            )
            st.session_state.winner2 = get_winner(
                (players[4], players[5]), (players[6], players[7]), c2_s1, c2_s2
            )
            st.session_state.round_completed = 1
            st.experimental_rerun()

    # Round 2: fixed matches based on Round 1 winners
    if st.session_state.round_completed == 1:
        st.header("🔵 Round 2 (Fixed)")
        st.write("**Court 1**: Player 9 & 10 vs Player 11 & 12")
        st.write(f"Teams: **{players[8]} & {players[9]}** vs **{players[10]} & {players[11]}**")
        c1_s1 = st.number_input("Court 1 - Team1 Score", min_value=0, max_value=4, key="r2c1_s1")
        c1_s2 = st.number_input("Court 1 - Team2 Score", min_value=0, max_value=4, key="r2c1_s2")
        st.write("**Court 2**: Winner of R1C1 vs Winner of R1C2")
        st.write(f"Team A: **{st.session_state.winner1[0]} & {st.session_state.winner1[1]}**")
        st.write(f"Team B: **{st.session_state.winner2[0]} & {st.session_state.winner2[1]}**")
        c2_s1 = st.number_input("Court 2 - Team1 Score", min_value=0, max_value=4, key="r2c2_s1")
        c2_s2 = st.number_input("Court 2 - Team2 Score", min_value=0, max_value=4, key="r2c2_s2")

        if st.button("Submit Round 2 Scores"):
            # Update scores
            for p in [players[8], players[9]]:
                st.session_state.scores[p] += c1_s1
            for p in [players[10], players[11]]:
                st.session_state.scores[p] += c1_s2
            for p in st.session_state.winner1:
                st.session_state.scores[p] += c2_s1
            for p in st.session_state.winner2:
                st.session_state.scores[p] += c2_s2
            st.session_state.round_completed = 2
            st.experimental_rerun()

    # Rounds 3 to 5: dynamic pairings based on rankings
    if st.session_state.round_completed >= 2:
        rounds = [3, 4, 5]
        for rnd in rounds:
            if f"round{rnd}_done" not in st.session_state:
                st.header(f"🔵 Round {rnd} (Based on Rankings)")
                # Sort players by current score descending
                ranked = sorted(st.session_state.scores.items(), key=lambda x: (-x[1], x[0]))
                ranked_players = [p[0] for p in ranked]
                # Select top 4 for Court 1, next 4 for Court 2
                t1 = (ranked_players[0], ranked_players[3])
                t2 = (ranked_players[1], ranked_players[2])
                t3 = (ranked_players[4], ranked_players[7])
                t4 = (ranked_players[5], ranked_players[6])
                st.write(f"**Court 1**: {t1[0]} & {t1[1]}  vs  {t2[0]} & {t2[1]}")
                c1_s1 = st.number_input(f"R{rnd}C1 - Team1 Score", min_value=0, max_value=4, key=f"r{rnd}c1_s1")
                c1_s2 = st.number_input(f"R{rnd}C1 - Team2 Score", min_value=0, max_value=4, key=f"r{rnd}c1_s2")
                st.write(f"**Court 2**: {t3[0]} & {t3[1]}  vs  {t4[0]} & {t4[1]}")
                c2_s1 = st.number_input(f"R{rnd}C2 - Team1 Score", min_value=0, max_value=4, key=f"r{rnd}c2_s1")
                c2_s2 = st.number_input(f"R{rnd}C2 - Team2 Score", min_value=0, max_value=4, key=f"r{rnd}c2_s2")

                if st.button(f"Submit Round {rnd} Scores"):
                    # Update scores for Court 1
                    for p in t1:
                        st.session_state.scores[p] += c1_s1
                    for p in t2:
                        st.session_state.scores[p] += c1_s2
                    # Update scores for Court 2
                    for p in t3:
                        st.session_state.scores[p] += c2_s1
                    for p in t4:
                        st.session_state.scores[p] += c2_s2
                    st.session_state[f"round{rnd}_done"] = True
                    st.experimental_rerun()

        # Once all rounds are done, display final leaderboard
        if all(st.session_state.get(f"round{rnd}_done", False) for rnd in rounds):
            st.header("🏆 Final Leaderboard")
            final_ranked = sorted(st.session_state.scores.items(), key=lambda x: (-x[1], x[0]))
            df = pd.DataFrame(final_ranked, columns=["Player", "Points"])
            st.table(df)
