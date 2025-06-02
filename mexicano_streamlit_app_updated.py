import streamlit as st

def create_round_matches(players, round_num, prev_winners=None):
    """Generate matches for each round based on Mexicano format and round number."""
    matches = []
    if round_num == 1:
        matches = [
            {"court": 1, "team1": (players[0], players[1]), "team2": (players[2], players[3]), "score": (0, 0), "winner": None},
            {"court": 2, "team1": (players[4], players[5]), "team2": (players[6], players[7]), "score": (0, 0), "winner": None},
        ]
    elif round_num == 2:
        if prev_winners and len(prev_winners) == 2:
            matches = [
                {"court": 1, "team1": (players[8], players[9]), "team2": (players[10], players[11]), "score": (0, 0), "winner": None},
                {"court": 2, "team1": prev_winners[0], "team2": prev_winners[1], "score": (0, 0), "winner": None},
            ]
    else:
        if prev_winners and len(prev_winners) == 4:
            matches = [
                {"court": 1, "team1": prev_winners[0], "team2": prev_winners[1], "score": (0, 0), "winner": None},
                {"court": 2, "team1": prev_winners[2], "team2": prev_winners[3], "score": (0, 0), "winner": None},
            ]
        elif prev_winners and len(prev_winners) == 2:
            matches = [
                {"court": 1, "team1": prev_winners[0], "team2": prev_winners[1], "score": (0, 0), "winner": None},
            ]
    return matches

def format_team(team):
    return f"{team[0]} & {team[1]}"

def main():
    st.title("🎾 Mexicano Format Tennis Tournament")

    default_players = "\n".join([f"player_{i}" for i in range(1, 13)])

    if "players" not in st.session_state:
        st.session_state.players = []
    if "round" not in st.session_state:
        st.session_state.round = 1
    if "matches" not in st.session_state:
        st.session_state.matches = []
    if "points" not in st.session_state:
        st.session_state.points = {}

    # Step 1: Input players (only once)
    if len(st.session_state.players) != 12:
        st.write("Enter exactly 12 unique player names (one per line):")
        players_text = st.text_area("Players", value=default_players, height=250)
        players_input = [p.strip() for p in players_text.splitlines() if p.strip()]

        if len(players_input) > 12:
            st.error("Please enter no more than 12 players.")
        elif len(set(players_input)) != len(players_input):
            st.error("Please enter unique player names only.")
        elif len(players_input) < 12:
            st.info("Please enter exactly 12 players.")
        else:
            st.session_state.players = players_input
            st.session_state.points = {p: 0 for p in players_input}
            st.rerun()
        return

    st.write(f"### 🏁 Round {st.session_state.round}")

    # Step 2: Generate matches if not created
    if not st.session_state.matches:
        prev_winners = None
        if st.session_state.round > 1:
            prev_winners = [m["winner"] for m in st.session_state.matches_prev_round if m["winner"]]
        st.session_state.matches = create_round_matches(st.session_state.players, st.session_state.round, prev_winners)
        st.session_state.matches_prev_round = st.session_state.matches.copy()

    # Step 3: Input match scores
    winners = []
    all_scores_entered = True

    for i, match in enumerate(st.session_state.matches):
        st.write(f"**Court {match['court']}**: {format_team(match['team1'])} vs {format_team(match['team2'])}")
        c1_score = st.number_input(f"Score for {format_team(match['team1'])}", min_value=0, max_value=4, key=f"c1_score_{i}")
        c2_score = st.number_input(f"Score for {format_team(match['team2'])}", min_value=0, max_value=4, key=f"c2_score_{i}")

        if c1_score == c2_score and c1_score != 0:
            st.warning("Ties are not allowed. Please enter a clear winner.")
            all_scores_entered = False
        elif c1_score == 0 and c2_score == 0:
            all_scores_entered = False
        else:
            if c1_score > c2_score:
                winner = match['team1']
            elif c2_score > c1_score:
                winner = match['team2']
            else:
                winner = None  # both are 0

            if winner:
                winners.append(winner)
                match['score'] = (c1_score, c2_score)
                match['winner'] = winner

    if st.button("✅ Submit Round Scores"):
        if not all_scores_entered:
            st.error("Please enter valid scores for all matches. Ties are not allowed.")
        else:
            for winner in winners:
                for p in winner:
                    st.session_state.points[p] += 1
            st.session_state.round += 1
            st.session_state.matches = []
            st.rerun()

    # Step 4: Show leaderboard
    st.write("### 🏆 Leaderboard")
    sorted_points = sorted(st.session_state.points.items(), key=lambda x: x[1], reverse=True)
    for p, pts in sorted_points:
        st.write(f"{p}: {pts} pt{'s' if pts != 1 else ''}")

if __name__ == "__main__":
    main()
