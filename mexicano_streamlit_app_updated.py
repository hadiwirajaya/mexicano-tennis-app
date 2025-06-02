import streamlit as st
import random

def mix_winners(team1, team2):
    """
    Given two winning teams (each a tuple of 2 players), return a new random pairing
    that mixes players from both teams, avoiding the original teammates.
    """
    p = list(team1 + team2)  # [p1, p2, p3, p4]
    mix1 = ((p[0], p[2]), (p[1], p[3]))
    mix2 = ((p[0], p[3]), (p[1], p[2]))
    return random.choice([mix1, mix2])

def create_round_matches(players, round_num, prev_winners=None):
    """
    Generate matches for each round based on Mexicano format:
    Round 1: Court 1 = players[0..3], Court 2 = players[4..7]
    Round 2: Court 1 = players[8..11], Court 2 mixes winners of Round 1
    Round 3+: Mix winners of previous round into 2 courts (or 1 court if only 2 remain)
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
        # Round 3+ : Mix the 4 winners of prior round into 2 courts, or final if only 2
        if prev_winners and len(prev_winners) == 4:
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
            # Final match
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
    return f"{team[0]} & {team[1]}"

def main():
    st.title("🎾 Mexicano Format Tennis/Padel Tournament (12 Players)")

    # Pre-fill 12 players
    default_players = "\n".join([f"player_{i}" for i in range(1, 13)])

    # Initialize session state once
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

    # Step 1: Enter 12 players
    if len(st.session_state.players) != 12:
        st.write("Enter exactly 12 unique player names (one per line):")
        players_text = st.text_area("Players", value=default_players, height=200)
        players_input = [p.strip() for p in players_text.splitlines() if p.strip()]

        if len(players_input) > 12:
            st.error("❌ Please enter no more than 12 players.")
        elif len(set(players_input)) != len(players_input):
            st.error("❌ Duplicate names detected. Please enter unique names.")
        elif len(players_input) < 12:
            st.info("ℹ️ Please enter exactly 12 players.")
        else:
            st.session_state.players = players_input
            st.session_state.points = {p: 0 for p in players_input}
            st.rerun()
        return  # Stop until 12 valid players are entered

    # Step 2: Show round header with match labels
    rn = st.session_state.round
    # Determine how many matches this round (1 or 2)
    # Round 1 & 2 always have 2 matches. Round 3+ could have 2 (4 winners) or 1 (2 winners).
    if rn <= 2:
        match_labels = f"Match {rn}.1 and Match {rn}.2"
    else:
        prev = st.session_state.matches_prev_round
        if prev and len(prev) == 1:
            match_labels = f"Match {rn}.1"
        else:
            match_labels = f"Match {rn}.1 and Match {rn}.2"
    st.write(f"### 🏁 Round {rn}: {match_labels}")

    # Step 3: If no matches exist for this round, generate them
    if not st.session_state.matches:
        prev_winners = None
        if rn > 1:
            prev_winners = [m["winner"] for m in st.session_state.matches_prev_round if m.get("winner")]
        st.session_state.matches = create_round_matches(
            st.session_state.players, rn, prev_winners
        )
        # We do NOT copy prev_round here; we wait until after scores are submitted

    # Step 4: Display matches and input scores
    winners = []
    all_scores_entered = True
    for idx, match in enumerate(st.session_state.matches):
        court = match["court"]
        t1 = match["team1"]
        t2 = match["team2"]
        st.write(f"**Court {court}**: {format_team(t1)}  vs  {format_team(t2)}")
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.number_input(f"Score for {format_team(t1)}", min_value=0, max_value=4, key=f"r{rn}_c{court}_s1")
        with c2:
            s2 = st.number_input(f"Score for {format_team(t2)}", min_value=0, max_value=4, key=f"r{rn}_c{court}_s2")

        # Check validity:
        if s1 == 0 and s2 == 0:
            all_scores_entered = False
            match["winner"] = None
        elif s1 == s2:
            st.warning("⚠️ Ties not allowed. Enter a clear winner.")
            all_scores_entered = False
            match["winner"] = None
        else:
            if s1 > s2:
                winner = t1
            else:
                winner = t2
            match["winner"] = winner
            match["score"] = (s1, s2)
            winners.append(winner)

        st.write("---")

    # Step 5: Submit button
    if st.button("✅ Submit Round Scores"):
        if not all_scores_entered or len(winners) != len(st.session_state.matches):
            st.error("❌ Please enter valid scores for every match, no ties allowed.")
        else:
            # Award 1 point for each winning player
            for team in winners:
                for p in team:
                    st.session_state.points[p] += 1

            # Store the fully-scored matches into matches_prev_round
            st.session_state.matches_prev_round = [
                { **m } for m in st.session_state.matches
            ]

            # Prepare next round
            st.session_state.round += 1
            st.session_state.matches = []
            st.rerun()

    # Step 6: Leaderboard (always visible)
    st.write("### 🏆 Leaderboard")
    sorted_pts = sorted(st.session_state.points.items(), key=lambda x: x[1], reverse=True)
    for name, pts in sorted_pts:
        display_name = f"**{name.upper()}**"
        st.write(f"{display_name}: {pts} pt{'s' if pts != 1 else ''}")

if __name__ == "__main__":
    main()
