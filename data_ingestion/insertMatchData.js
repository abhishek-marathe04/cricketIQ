const pool = require('./db');
const fs = require('fs');
const path = require("path");
const { shouldProcessMatch } = require('./matchFilter');

// const filePath = path.join(__dirname, "dataset/335982.json"); // Update with actual file name
// const client = await pool.connect();
const DATA_FOLDER = "./dataset/matches_data"; // Update with the actual folder path

async function insertMatch(matchInfo) {
    try {
        const query = `
        INSERT INTO matches (
          match_id, season_id, balls_per_over, city, match_date, event_name, match_number,
          gender, match_type, format, overs, season, team_type, venue, toss_winner,
          team1, team2, toss_decision, match_winner, win_by_runs, win_by_wickets, player_of_match, result
        ) 
        VALUES (
          $1, $2, $3, $4, $5, $6,
          $7, $8, $9, $10, $11, $12, $13, $14,
          $15, $16, $17, $18, $19, $20, $21, $22, $23
        )
        RETURNING match_id;
      `;

        const values = [
            matchInfo.match_id, matchInfo.season_id, matchInfo.balls_per_over, matchInfo.city, matchInfo.match_date,
            matchInfo.event_name, matchInfo.match_number, matchInfo.gender, matchInfo.match_type,
            matchInfo.format, matchInfo.overs, matchInfo.season, matchInfo.team_type,
            matchInfo.venue, matchInfo.toss_winner, matchInfo.team1, matchInfo.team2,
            matchInfo.toss_decision, matchInfo.match_winner, matchInfo.win_by_runs,
            matchInfo.win_by_wickets, matchInfo.player_of_match, matchInfo.result
        ];

        const res = await pool.query(query, values);
        console.log(`✅ Match inserted with ID: ${res.rows[0].match_id}`);
    } catch (error) {
        console.error("❌ Error inserting match data:", error.message);
    } finally {
        // client.release();
    }
}

async function getTeamId(teamName) {
    // Step 1: Check if the team name exists in team_aliases
    console.log(`Get Team Id for ${teamName}`)
    const aliasRes = await pool.query(
        "SELECT team_id FROM team_aliases WHERE alias_name = $1",
        [teamName]
    );

    let teamId;
    if (aliasRes.rows.length > 0) {
        teamId = aliasRes.rows[0].team_id; // Use the mapped team_id

        console.log(`Found Team : ${teamName} already exists with id ${teamId}`)

    } else {
        console.log(`Getting error while finding ${teamName}`)
    }
    console.log(`Returning response for : ${teamName} with id ${teamId}`)
    return teamId;
}

async function getPlayerId(playerName) {
    // Step 1: Check if the team name exists in team_aliases
    const playerRes = await pool.query(
        "SELECT player_id FROM players WHERE player_name = $1",
        [playerName]
    );

    let playerId;
    if (playerRes.rows.length > 0) {

        playerId = playerRes.rows[0].player_id; // Use the mapped team_id
        console.log(`Found Player : ${playerName} already exists with id ${playerId}`)

    } else {
        throw Error;
    }
    return playerId;
}

async function processMatchData(matchId, matchInfo){
    console.log(`Processing match id ${matchId}`)
    console.log({matchInfo})

    const team1Id = await getTeamId(matchInfo.teams[0])
    const team2Id = await getTeamId(matchInfo.teams[1])

    const toss_winner = matchInfo.toss.winner === matchInfo.teams[0] ? team1Id : team2Id
    const match_winner = matchInfo.outcome.winner === matchInfo.teams[0] ? team1Id : team2Id

    const player_of_match_id = matchInfo.player_of_match ? await getPlayerId(matchInfo.player_of_match[0]) : null

    const matchJson = {
        match_id: matchId,
        season_id: parseInt(matchInfo.season),
        balls_per_over: matchInfo.balls_per_over,
        city: matchInfo.city,
        match_date: matchInfo.dates[0],
        event_name: matchInfo.event.name,
        match_number: matchInfo.event.match_number,
        gender: matchInfo.gender,
        match_type: matchInfo.match_type,
        format: matchInfo.match_type,
        overs: matchInfo.overs,
        season: matchInfo.season,
        team_type: matchInfo.team_type,
        venue: matchInfo.venue,
        toss_winner: toss_winner,
        team1: team1Id,
        team2: team2Id,
        toss_decision: matchInfo.toss.decision,
        match_winner: match_winner,
        win_by_runs: matchInfo.outcome?.by?.runs || null,
        win_by_wickets: matchInfo.outcome?.by?.wickets || null,
        result: matchInfo.outcome.result || 'win',
        player_of_match: player_of_match_id
    };

    console.log({ matchJson })
    await insertMatch(matchJson)
}

async function main() {

    const files = fs.readdirSync(DATA_FOLDER); // Get all files in the folder

    console.log(files.length)
    for (const file of files) {
        if (path.extname(file) === ".json") {
            console.log(`Processing file: ${file}`);

            const filePath = path.join(DATA_FOLDER, file);
            const jsonData = JSON.parse(fs.readFileSync(filePath, "utf8"));
            // Extract match_id
            const matchId = parseInt(path.basename(file, '.json'), 10);

            console.log("Match ID:", matchId); // Output: 12345

            const matchInfo = jsonData.info

            if(shouldProcessMatch(matchId)){
                await processMatchData(matchId, matchInfo)
            }
        }
    }

}

main()