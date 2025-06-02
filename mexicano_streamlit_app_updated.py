import streamlit as st
import random

def mix_winners(team1, team2):
    """
    Given two winning teams (each a tuple of 2 players), return a new random pairing
    that mixes players from both teams, avoiding the original teammates.
    E.g., from (1,2) and (5,6), produce either ((1,5),(2,6)) or ((1,6),(2,5)).
    """
    p = list(team1 + team2)  # [1,2,5,6]
    mix1 = ((p[0], p[2]), (p[1], p[3]))
    mix2 = ((p[0], p[3]), (p[1], p[2]))
    return random.choice([mix1, mix2])

def create_round_matches(players, round_num, prev_winners=None):
    """
    Generate matches for each round based on Mexicano format:
    - Round 1: Court 1 = players[0..3], Court 2 = players[4..7]
    - Round 2: Court 1 = players[8..11], Court 2 mixes winners of Round 1
    - Round 3+: Always mix winners of previous round (4 winners) into 2 courts.
      If only 2 winners remain, play single match on Court 1.
    """
    matches = []
    if round_num == 1:
        matches = [
            {
                "court": 1,
                "team1": (players[0], players[1]),
                "team2": (players[2], players[3]),
                "score": (0, 0),
                "winner": None
            },
            {
                "court": 2,
                "team1": (players[4], players[5]),
                "team2": (players[6], players[7]),
                "score": (0, 0),
                "winner": None
            },
        ]
    elif round_num == 2:
        # Gather exactly 2 winners from Round 1
        if prev_winners and len(prev_winners) == 2:
            mixed1, mixed2 = mix_winners(prev_winners[0], prev_winners[1])
            matches = [
                {
                    "court": 1,
                    "team1": (players[8], players[9]),
                    "team2": (players[10], players[11]),
                    "score": (0, 0),
                    "winner": None
                },
                {
                    "court": 2,
                    "team1": mixed1,
                    "team2": mixed2,
                    "score": (0, 0),
                    "winner": None
                },
            ]
    else:
        # Round 3+: mix the 4 winners of the prior round
        if prev_winners and len(prev_winners) == 4:
            # prev_winners is a list of 4 two-tuples
            matches = [
                {
                    "court": 1,
                    "team1": prev_winners[0],
                    "team2": prev_winners[1],
                    "score": (0, 0),
                    "winner": None
                },
                {
                    "court": 2,
                    "team1": prev_winners[2],
                    "team2": prev_winners[3],
                    "score": (0, 0),
                    "winner": None
                },
            ]
        elif prev_winners and len(prev_winners) == 2:
            # Final: only 2 teams remain → single match on Court 1
            matches = [
                {
                    "court": 1,
                    "team1": prev_winners[0],
                    "team2": prev_winners[1],
                    "score": (0, 0),
                    "winner": None
                }
            ]
    return matches

def format_team(team):
    """Return a readable string for a team tuple."""
    return f"{team[0]} & {team[1]}"

def main():
    st.title("🎾 Mexicano Tournament (12 Players, 2 Courts)")

    # Predefine default player names
    default_players = "\n".join([f"player_{i}" for i in range(1, 13)])

    # Initialize session state
    if "players" not in st.session_state:
        st.session_state.players = []
    if "round" not in st.session_state:
        st.session_state.round = 1
    if "matches" not in st.session_state:
        st.session_state.matches = []
    if "matches_prev_round" not in st.session_state:
        st.session_state.matches_prev_round = []
    if "points" not in st.session_state:
        st.session_state.points = {}

    # Step 1: Input players (only until 12 are set)
    if len(st.session_state.players) != 12:
        st.write("Enter exactly 12 unique player names (one per line):")
        players_text = st.text_area("Players", value=default_players, height=250)
        players_input = [p.strip() for p in players_text.splitlines() if p.strip()]

        if len(players_input) > 12:
            st.error("❌ Please enter no more than 12 players.")
        elif len(set(players_input)) != len(players_input):
            st.error("❌ Duplicate names detected. Please enter unique names.")
        elif len(players_input) < 12:
            st.info("ℹ️ Please enter exactly 12 players.")
        else:
            # Save to session and initialize points
            st.session_state.players = players_input
            st.session_state.points = {p: 0 for p in players_input}
            # After setting players, rerun to show Round 1
            st.rerun()
        return  # Stop here until exactly 12 players

    # Step 2: Show round header with match labels
    rn = st.session_state.round
    # Determine number of matches in this round (1 or 2)
    num_matches = 2
    if rn > 2:
        # Rounds ≥ 3 may have just 1 match if only 2 teams remain
        if st.session_state.matches_prev_round and len(st.session_state.matches_prev_round) == 1:
            num_matches = 1
    match_labels = " and ".join([f"Match {rn}.{i+1}" for i in range(num_matches)])
    st.write(f"### 🏁 Round {rn}: {match_labels}")

    # Step 3: Generate matches if not already created for this round
    if not st.session_state.matches:
        prev_winners = None
        if rn > 1:
            # Collect winners from previous round
            prev_winners = [m["winner"] for m in st.session_state.matches_prev_round if m["winner"]]
        st.session_state.matches = create_round_matches(
            st.session_state.players, rn, prev_winners
        )
        # Keep a copy for next round’s logic
        st.session_state.matches_prev_round = [m.copy() for m in st.session_state.matches]

    # Step 4: Display matches & input scores
    winners = []
    all_scores_entered = True
    for idx, match in enumerate(st.session_state.matches):
        court = match["court"]
        t1 = match["team1"]
        t2 = match["team2"]
        st.write(f"**Court {court}**: {format_team(t1)}  vs  {format_team(t2)}")
        col1, col2 = st.columns(2)
        with col1:
            score1 = st.number_input(
                f"Score for {format_team(t1)}", min_value=0, max_value=4, key=f"r{rn}_c{court}_s1"
            )
        with col2:
            score2 = st.number_input(
                f"Score for {format_team(t2)}", min_value=0, max_value=4, key=f"r{rn}_c{court}_s2"
            )

        # Check for no-entered scores
        if score1 == 0 and score2 == 0:
            all_scores_entered = False
            match["winner"] = None
        # Prevent ties
        elif score1 == score2:
            st.warning("⚠️ Ties not allowed. Enter a clear winner.")
            all_scores_entered = False
            match["winner"] = None
        else:
            if score1 > score2:
                winner = t1
            else:
                winner = t2
            match["winner"] = winner
            match["score"] = (score1, score2)
            winners.append(winner)

        st.write("---")

    # Step 5: Submit button for this round’s scores
    if st.button("✅ Submit Round Scores"):
        if not all_scores_entered or len(winners) != len(st.session_state.matches):
            st.error("❌ Please enter valid scores for all matches (no ties).")
        else:
            # Award 1 point to each winning player
            for team in winners:
                for p in team:
                    st.session_state.points[p] += 1

            # Advance to next round
            st.session_state.round += 1
            # Clear current matches so they regenerate next round
            st.session_state.matches = []
            st.rerun()

    # Step 6: Always show current leaderboard
    st.write("### 🏆 Leaderboard")
    sorted_pts = sorted(
        st.session_state.points.items(), key=lambda x: x[1], reverse=True
    )
    for name, pts in sorted_pts:
        display_name = f"**{name.upper()}**"
        st.write(f"{display_name}: {pts} pt{'s' if pts != 1 else ''}")

if __name__ == "__main__":
    main()
