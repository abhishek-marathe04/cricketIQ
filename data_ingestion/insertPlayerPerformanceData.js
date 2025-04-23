const pool = require('./db');
const fs = require('fs');
const path = require("path");

// const filePath = path.join(__dirname, "dataset/335982.json"); // Update with actual file name
// const client = await pool.connect();
const DATA_FOLDER = "./dataset/matches_data/test"; // Update with the actual folder path

async function insertPlayerPerformance(performance) {
  const query = `
    INSERT INTO player_performance (
      match_id, player_id, player_name,
      runs_scored, balls_faced, fours, sixes,
      wickets_taken, extras_bowled, dot_balls_bowled, overs_bowled, maidens, runs_conceded,
      catches, stumpings, run_outs,
      team_id, team_name, opponent_team_id, opponent_team_name
    )
    VALUES (
      $1, $2, $3,
      $4, $5, $6, $7,
      $8, $9, $10, $11,
      $12, $13,
      $14, $15, $16, $17
    )
    RETURNING performance_id;
  `;

  const values = [
    performance.match_id,
    performance.player_id,
    performance.player_name,
    performance.runs_scored,
    performance.balls_faced,
    performance.fours,
    performance.sixes,
    performance.wickets_taken,
    performance.extras_conceded,
    performance.dot_balls_bowled,
    performance.overs_bowled,
    performance.maidens,
    performance.runs_conceded,
    performance.catches,
    performance.stumpings,
    performance.run_outs,
    performance.team_id,
    performance.team_name,
    performance.opponent_team_id,
    performance.opponent_team_name
  ];

  try {
    const res = await pool.query(query, values);
    console.log('Inserted with performance_id:', res.rows[0].performance_id);
  } catch (err) {
    console.error('Error inserting performance:', err.message);
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

async function getPlayerInfo(playerName) {
    // Step 1: Check if the team name exists in team_aliases
    console.log({playerName})
    const playerRes = await pool.query(
        "SELECT player_id, bat_style, bowl_style FROM players WHERE player_name = $1",
        [playerName]
    );

    let playerId, batStyle, bowlStyle;
    if (playerRes.rows.length > 0) {
        
        playerId = playerRes.rows[0].player_id; // Use the mapped team_id
        batStyle = playerRes.rows[0].bat_style; // Use the mapped team_id
        bowlStyle = playerRes.rows[0].bowl_style; // Use the mapped team_id
        console.log(`Found Player : ${playerName} already exists with id ${playerId}`)

    } else {
        throw Error;
    }
    return {
        playerId,
        batStyle,
        bowlStyle
    };
}

async function main() {

    const files = fs.readdirSync(DATA_FOLDER); // Get all files in the folder

    for (const file of files) {
        if (path.extname(file) === ".json") {
            console.log(`Processing file: ${file}`);

            const filePath = path.join(DATA_FOLDER, file);
            const jsonData = JSON.parse(fs.readFileSync(filePath, "utf8"));
            // Extract match_id
            const matchId = parseInt(path.basename(file, '.json'), 10);

            console.log("Match ID:", matchId); // Output: 12345

            const matchInfo = jsonData.info

            // console.log({matchInfo})


            const seasonId = matchInfo.season
            const team1Id = await getTeamId(matchInfo.teams[0])
            const team2Id = await getTeamId(matchInfo.teams[1])

            const team1Name = matchInfo.teams[0]
            const team2Name = matchInfo.teams[1]

            const toss_winner = matchInfo.toss.winner === matchInfo.teams[0] ? team1Id : team2Id
            const match_winner = matchInfo.outcome.winner === matchInfo.teams[0] ? team1Id : team2Id

            // const player_of_match_id = matchInfo.player_of_match ? await getPlayerId(matchInfo.player_of_match[0]) : null

            const samplePlayerJson = {
              "match_id": matchId,
              "player_id": 0,
              "player_name": "",
              "runs_scored": 0,
              "balls_faced": 0,
              "fours": 0,
              "sixes": 0,
              "wickets_taken": 0,
              "balls_bowled": 0,
              "overs_bowled": 0,
              "extras_conceded": 0,
              "dot_balls_bowled": 0,
              "maidens": 0,
              "runs_conceded": 0,
              "run_outs": 0,
              "catches": 0,
              "stumpings": 0,
              "team_id": 0,
              "team_name": "",
              "opponent_team_id": 0,
              "opponent_team_name": ""
            }

            const nonBowlerWickets = [
              'run out', 'retired hurt', 'timed out', 'obstructing the field'
            ]

            let playersData = {}

            let inningsCounter = 0;
            for (const inningObj of jsonData.innings) {
                inningsCounter++;
                const inningsNum = inningsCounter;
                const team_batting =  await getTeamId(inningObj.team)
                const team_batting_name = inningObj.team
                const team_bowling = team_batting === team1Id ? team2Id : team1Id
                const team_bowling_name = team_batting_name === team1Name ? team2Name : team1Name
                const is_super_over = inningObj.super_over ? true : false
            
                for (const over of inningObj.overs) {
                  const over_number = over.over;
            
                  for (const [index, delivery] of over.deliveries.entries()) {

                    
                    
                    const no_ball_runs = delivery.extras?.noballs || 0
                    const wide_runs = delivery.extras?.wides || 0
                    const isWide = wide_runs ? true : false
                    const isNoBall = no_ball_runs ? true : false
                    const wicket_kind = delivery.wickets ? delivery.wickets[0].kind : null

                    if(!playersData[delivery.batter]) {
                      const batter = await getPlayerInfo(delivery.batter)
                      playersData[delivery.batter] = { ...samplePlayerJson}
                      playersData[delivery.batter].player_id = batter.playerId
                      playersData[delivery.batter].player_name = delivery.batter
                    }
                    
                    playersData[delivery.batter].runs_scored += delivery.runs.batter
                    
                    if (delivery.runs.batter === 4){
                      playersData[delivery.batter].fours += 1
                    }

                    if (delivery.runs.batter === 6){
                      playersData[delivery.batter].sixes += 1
                    }

                    if (!delivery.runs.extras){
                      playersData[delivery.batter].balls_faced += 1
                    }
                    

                    if(!playersData[delivery.bowler]) {
                      const bowler = await getPlayerInfo(delivery.bowler)
                      playersData[delivery.bowler] = { ...samplePlayerJson}
                      playersData[delivery.bowler].player_id = bowler.playerId
                      playersData[delivery.bowler].player_name = delivery.bowler
                    }


                    if(wicket_kind && !nonBowlerWickets.includes(wicket_kind.toLowerCase())){
                      playersData[delivery.bowler].wickets_taken += 1
                    }

                    if (delivery.runs.extras && (isWide || isNoBall)){
                      playersData[delivery.bowler].extras_conceded += delivery.runs.extras
                      playersData[delivery.bowler].runs_conceded += delivery.runs.extras
                    } else if(delivery.runs.extras){
                      continue;
                    } else {
                      playersData[delivery.bowler].runs_conceded += delivery.runs.batter
                      playersData[delivery.bowler].balls_bowled += 1
                      if(delivery.runs.batter === 0){
                        playersData[delivery.bowler].dot_balls_bowled += 1
                      }
                    }
                    
                     
                    const fielders = (delivery.wickets && delivery.wickets[0].fielders ) || []
                    
                    if(fielders.length){
                      for(let fielder of fielders){
                        console.log({fielder})
                        if(!playersData[fielder.name]) {
                          const fielderInfo = await getPlayerInfo(fielder.name)
                          playersData[fielder.name] = { ...samplePlayerJson}
                          playersData[fielder.name].player_id = fielderInfo.playerId
                        }
                      }

                      for(let fielder of fielders){
                        if(wicket_kind === 'caught'){
                          console.log({fielder})
                          playersData[fielder.name].catches += 1
                        } else if(wicket_kind === 'stumped') {
                          playersData[fielder.name].stumpings += 1
                        } else if(wicket_kind === 'run out'){
                          playersData[fielder.name].run_outs += 1
                        }
                      }
                    }

                    playersData[delivery.batter].team_id = team_batting
                    playersData[delivery.batter].team_name = team_batting_name
                    playersData[delivery.batter].opponent_team_id = team_bowling
                    playersData[delivery.batter].opponent_team_name = team_bowling_name

                    playersData[delivery.batter].team_id = team_bowling
                    playersData[delivery.batter].team_name = team_bowling_name
                    playersData[delivery.batter].opponent_team_id = team_batting
                    playersData[delivery.batter].opponent_team_name = team_batting_name
                    
                    
                  }
                }
              }

              console.log({playersData})
                try {
                // await insertBallStat(ball);
                } catch (err) {
                  console.error('Insert error:', err.message);
                }
        }
    }

}

main()