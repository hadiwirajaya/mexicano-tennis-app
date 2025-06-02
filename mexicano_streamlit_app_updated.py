import streamlit as st
import random

# Initialize session state
if "players" not in st.session_state:
    st.session_state["players"] = []
if "round" not in st.session_state:
    st.session_state["round"] = 1
if "matches" not in st.session_state:
    st.session_state["matches"] = []
if "scores" not in st.session_state:
    st.session_state["scores"] = {}

st.title("🎾 Mexicano Tennis Format")

# Step 1: Player Input
with st.form("player_input"):
    player_input = st.text_area("Enter 12 player names (one per line):", height=250)
    submitted = st.form_submit_button("Start Tournament")

if submitted:
    players = player_input.strip().split("\n")
    if len(players) != 12:
        st.error("You must enter exactly 12 players.")
    else:
        random.shuffle(players)
        st.session_state["players"] = players
        st.session_state["scores"] = {p: 0 for p in players}
        st.session_state["round"] = 1
        st.session_state["matches"] = []

# Display players and scores
if st.session_state["players"]:
    st.subheader("Current Scores")
    sorted_scores = sorted(st.session_state["scores"].items(), key=lambda x: -x[1])
    for p, s in sorted_scores:
        st.write(f"{p}: {s} points")

    # Step 2: Display Matches for Current Round
    st.subheader(f"Round {st.session_state['round']} Matches")

    match_results = []
    players = st.session_state["players"]
    scores = st.session_state["scores"]

    # Generate matches
    if st.session_state["round"] == 1:
        round_matches = [
            [players[0], players[1], players[2], players[3]],
            [players[4], players[5], players[6], players[7]],
        ]
    elif st.session_state["round"] == 2:
        round_matches = [
            [players[8], players[9], players[10], players[11]],
            # Match winners from previous round
            sorted_players = sorted(scores.items(), key=lambda x: -x[1])
            top8 = [p[0] for p in sorted_players[:8]]
            [top8[0], top8[1], top8[2], top8[3]]
        ]
    else:
        sorted_players = sorted(scores.items(), key=lambda x: -x[1])
        player_pool = [p[0] for p in sorted_players]
        round_matches = []
        for i in range(0, 12, 4):
            if i+3 < len(player_pool):
                round_matches.append([
                    player_pool[i], player_pool[i+1],
                    player_pool[i+2], player_pool[i+3],
                ])

    # Step 3: Input scores for each match
    with st.form(f"round_{st.session_state['round']}_form"):
        for idx, match in enumerate(round_matches):
            st.markdown(f"**Court {idx+1}: {match[0]} & {match[1]} vs {match[2]} & {match[3]}**")
            c1_s1 = st.number_input(f"{match[0]} & {match[1]} score", min_value=0, max_value=4, key=f"{idx}_team1")
            c1_s2 = st.number_input(f"{match[2]} & {match[3]} score", min_value=0, max_value=4, key=f"{idx}_team2")
            match_results.append((match, c1_s1, c1_s2))

        submitted_scores = st.form_submit_button("Submit Scores")

    # Step 4: Update scores
    if submitted_scores:
        for match, s1, s2 in match_results:
            st.session_state["scores"][match[0]] += s1
            st.session_state["scores"][match[1]] += s1
            st.session_state["scores"][match[2]] += s2
            st.session_state["scores"][match[3]] += s2
            st.session_state["matches"].append((match, s1, s2))

        st.success(f"Scores submitted for Round {st.session_state['round']}!")
        st.session_state["round"] += 1
        st.experimental_rerun()
