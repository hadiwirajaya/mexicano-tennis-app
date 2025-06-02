import streamlit as st
import random

def init_session():
    if "players" not in st.session_state:
        st.session_state.players = []
    if "round" not in st.session_state:
        st.session_state.round = 1
    if "points" not in st.session_state:
        st.session_state.points = {}
    if "matches" not in st.session_state:
        st.session_state.matches = []

def create_pairs(players_sorted):
    pairs = []
    for i in range(0, 8, 4):
        group = players_sorted[i:i+4]
        if len(group) < 4:
            break
        pairs.append( ((group[0], group[1]), (group[2], group[3])) )
    return pairs

def schedule_matches():
    players = st.session_state.players
    points = st.session_state.points
    round_num = st.session_state.round

    if round_num == 1:
        selected_players = players[:8]
        random.shuffle(selected_players)
    else:
        sorted_players = sorted(points.items(), key=lambda x: x[1], reverse=True)
        sorted_players = [p for p, pts in sorted_players]
        selected_players = sorted_players[:8]

    pairs = create_pairs(selected_players)
    st.session_state.matches = []

    court_num = 1
    for pair in pairs:
        st.session_state.matches.append({
            "court": court_num,
            "teams": pair,
            "score": None,
            "winner": None
        })
        court_num += 1

def input_scores():
    new_matches = []
    winners = []
    for match in st.session_state.matches:
        court = match["court"]
        t1 = match["teams"][0]
        t2 = match["teams"][1]

        st.write(f"**Court {court}**")
        st.write(f"Team 1: {t1[0]} & {t1[1]}")
        st.write(f"Team 2: {t2[0]} & {t2[1]}")

        col1, col2 = st.columns(2)
        with col1:
            s1 = st.number_input(f"Score Team 1 (0-4)", min_value=0, max_value=4, key=f"score_{court}_1", value=0)
        with col2:
            s2 = st.number_input(f"Score Team 2 (0-4)", min_value=0, max_value=4, key=f"score_{court}_2", value=0)

        match["score"] = (s1, s2)

        if s1 > s2:
            winner = t1
        elif s2 > s1:
            winner = t2
        else:
            winner = None

        match["winner"] = winner
        new_matches.append(match)
        winners.append(winner)

    st.session_state.matches = new_matches
    return winners

def update_points(winners):
    for winner in winners:
        if winner is None:
            continue
        for player in winner:
            st.session_state.points[player] = st.session_state.points.get(player, 0) + 1

def main():
    st.title("Mexicano Format Padel Scheduler - 12 Players, 2 Courts")

    init_session()

    if not st.session_state.players:
        st.write("Enter exactly 12 unique player names (one per line):")
        players_text = st.text_area("Players:", height=300)
        if st.button("Submit Players"):
            players = [p.strip() for p in players_text.strip().split("\n") if p.strip()]
            if len(players) != 12:
                st.error("Please enter exactly 12 player names.")
            elif len(set(players)) != 12:
                st.error("Duplicate names detected. Please enter unique names.")
            else:
                st.session_state.players = players
                st.session_state.points = {p:0 for p in players}
                st.session_state.round = 1
                schedule_matches()
                st.experimental_rerun()
    else:
        st.write(f"### Round {st.session_state.round}")
        if not st.session_state.matches:
            schedule_matches()

        winners = input_scores()

        if st.button("Submit Round Scores"):
            if any(m["winner"] is None for m in st.session_state.matches):
                st.error("No ties allowed. Please enter a valid winner for each match.")
            else:
                update_points(winners)
                st.success("Scores submitted!")

                st.write("### Current Points")
                for p, pts in sorted(st.session_state.points.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"{p}: {pts}")

                st.session_state.round += 1
                schedule_matches()
                st.experimental_rerun()

        st.write("### Current Points")
        for p, pts in sorted(st.session_state.points.items(), key=lambda x: x[1], reverse=True):
            st.write(f"{p}: {pts}")

if __name__ == "__main__":
    main()
