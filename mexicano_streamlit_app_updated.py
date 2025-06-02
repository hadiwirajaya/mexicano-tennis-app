import streamlit as st
import random

def init_session_state():
    if "players" not in st.session_state:
        st.session_state.players = []
    if "round" not in st.session_state:
        st.session_state.round = 1
    if "points" not in st.session_state:
        st.session_state.points = {}
    if "matches" not in st.session_state:
        st.session_state.matches = []

def create_round_matches(players):
    # For round 1 and others: 
    # Court 1: players 1 & 2 vs 3 & 4
    # Court 2: players 5 & 6 vs 7 & 8
    # Next round: Court 1: players 9 & 10 vs 11 & 12
    # Court 2: winner of Court1 vs winner of Court2
    
    matches = []
    if st.session_state.round == 1:
        # First 8 players in two matches on 2 courts
        matches.append({
            "court": 1,
            "team1": (players[0], players[1]),
            "team2": (players[2], players[3]),
            "score": (0,0),
            "winner": None
        })
        matches.append({
            "court": 2,
            "team1": (players[4], players[5]),
            "team2": (players[6], players[7]),
            "score": (0,0),
            "winner": None
        })
    elif st.session_state.round == 2:
        # Court 1: players 9,10 vs 11,12
        matches.append({
            "court": 1,
            "team1": (players[8], players[9]),
            "team2": (players[10], players[11]),
            "score": (0,0),
            "winner": None
        })
        # Court 2: winners from previous round matches
        prev_winners = [m["winner"] for m in st.session_state.matches if m["winner"]]
        if len(prev_winners) == 2:
            matches.append({
                "court": 2,
                "team1": prev_winners[0],
                "team2": prev_winners[1],
                "score": (0,0),
                "winner": None
            })
    else:
        # For later rounds, you can customize or stop
        matches = []

    return matches

def update_points(winners):
    for winner in winners:
        if winner is None:
            continue
        for player in winner:
            st.session_state.points[player] = st.session_state.points.get(player, 0) + 1

def main():
    st.title("Mexicano Format Padel/Tennis Scheduler (12 players, 2 courts)")

    init_session_state()

    if not st.session_state.players:
        st.write("Enter exactly 12 unique player names, one per line:")
        players_input = st.text_area("Players:", height=280)

        if st.button("Submit Players"):
            players = [p.strip() for p in players_input.strip().split("\n") if p.strip()]
            if len(players) != 12:
                st.error("Please enter exactly 12 players.")
            elif len(set(players)) != 12:
                st.error("Duplicate player names detected.")
            else:
                st.session_state.players = players
                st.session_state.points = {p: 0 for p in players}
                st.session_state.round = 1
                st.session_state.matches = create_round_matches(players)
                st.experimental_rerun()
    else:
        st.write(f"### Round {st.session_state.round}")
        
        winners = []
        for match in st.session_state.matches:
            st.write(f"**Court {match['court']}**")
            st.write(f"Team 1: {match['team1'][0]} & {match['team1'][1]}")
            st.write(f"Team 2: {match['team2'][0]} & {match['team2'][1]}")

            col1, col2 = st.columns(2)
            with col1:
                score1 = st.number_input(f"Score Team 1 (Court {match['court']})", 0, 4, key=f"s1_{match['court']}")
            with col2:
                score2 = st.number_input(f"Score Team 2 (Court {match['court']})", 0, 4, key=f"s2_{match['court']}")

            if score1 == score2:
                st.warning("Ties not allowed. Please enter a winner.")
                match["winner"] = None
            elif score1 > score2:
                match["winner"] = match["team1"]
            else:
                match["winner"] = match["team2"]

            match["score"] = (score1, score2)
            winners.append(match["winner"])

            st.write("---")

        if st.button("Submit Round Scores"):
            if None in winners:
                st.error("All matches must have a winner before submitting.")
            else:
                update_points(winners)
                st.success("Scores submitted!")

                # Show points table
                st.write("### Current Points:")
                sorted_pts = sorted(st.session_state.points.items(), key=lambda x: x[1], reverse=True)
                for p, pts in sorted_pts:
                    st.write(f"{p}: {pts}")

                # Advance round
                st.session_state.round += 1
                # Schedule new round matches
                st.session_state.matches = create_round_matches(st.session_state.players)
                st.experimental_rerun()

        st.write("### Current Points:")
        sorted_pts = sorted(st.session_state.points.items(), key=lambda x: x[1], reverse=True)
        for p, pts in sorted_pts:
            st.write(f"{p}: {pts}")

if __name__ == "__main__":
    main()
