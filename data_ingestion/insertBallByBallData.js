const pool = require('./db');
const fs = require('fs');
const path = require("path");
const { shouldProcessMatch } = require('./matchFilter');

// const filePath = path.join(__dirname, "dataset/335982.json"); // Update with actual file name
// const client = await pool.connect();
const DATA_FOLDER = "./dataset/matches_data"; // Update with the actual folder path

async function insertBallStat(data) {
    const query = `
      INSERT INTO ball_by_ball_stats (
        season_id, match_id, batter, bowler, non_striker,
        team_batting, team_bowling, over_number, ball_number,
        batter_runs, extras, total_runs,
        batsman_type, bowler_type, player_out, fielders_involved,
        is_wicket, is_wide_ball, is_no_ball, is_leg_bye, is_bye, is_penalty,
        wide_ball_runs, no_ball_runs, leg_bye_runs, bye_runs, penalty_runs,
        wicket_kind, is_super_over, innings
      )
      VALUES (
        $1, $2, $3, $4, $5, $6,
        $7, $8, $9, $10,
        $11, $12, $13,
        $14, $15,
        $16, $17, $18, $19, $20, $21,
        $22, $23, $24, $25, $26,
        $27, $28, $29, $30
      )
    `;
  
    const values = [
      data.season_id,
      data.match_id,
      data.batter,
      data.bowler,
      data.non_striker,
      data.team_batting,
      data.team_bowling,
      data.over_number,
      data.ball_number,
      data.batter_runs,
      data.extras,
      data.total_runs,
      data.batsman_type,
      data.bowler_type,
      data.player_out,
      JSON.stringify(data.fielders_involved),
      data.is_wicket,
      data.is_wide_ball,
      data.is_no_ball,
      data.is_leg_bye,
      data.is_bye,
      data.is_penalty,
      data.wide_ball_runs,
      data.no_ball_runs,
      data.leg_bye_runs,
      data.bye_runs,
      data.penalty_runs,
      data.wicket_kind,
      data.is_super_over,
      data.innings
    ];
  
    try {
      await pool.query(query, values);
      console.log('Ball data inserted successfully.');
    } catch (err) {
      console.error('Error inserting ball data:', err.message);
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

async function processBallByBallData(matchId, matchInfo, inningsData){
  console.log(`Processing ball by data for  match ${matchId}`)
  const seasonId = matchInfo.season
  const team1Id = await getTeamId(matchInfo.teams[0])
  const team2Id = await getTeamId(matchInfo.teams[1])

  const toss_winner = matchInfo.toss.winner === matchInfo.teams[0] ? team1Id : team2Id
  const match_winner = matchInfo.outcome.winner === matchInfo.teams[0] ? team1Id : team2Id

  // const player_of_match_id = matchInfo.player_of_match ? await getPlayerId(matchInfo.player_of_match[0]) : null

  let inningsCounter = 0;
  for (const inningObj of inningsData) {
      inningsCounter++;
      const inningsNum = inningsCounter;
      const team_batting =  await getTeamId(inningObj.team)
      const team_bowling = team_batting === team1Id ? team2Id : team1Id
      const is_super_over = inningObj.super_over ? true : false
  
      for (const over of inningObj.overs) {
        const over_number = over.over;
  
        for (const [index, delivery] of over.deliveries.entries()) {

          const batter = await getPlayerInfo(delivery.batter)
          const bowler = await getPlayerInfo(delivery.bowler)
          
          const leg_bye_runs = delivery.extras?.legbyes || 0
          const wide_runs = delivery.extras?.wides || 0
          const no_ball_runs = delivery.extras?.noballs || 0
          const byes_runs = delivery.extras?.byes || 0
          const penalty_runs = delivery.extras?.penalty || 0

          const isLegBye = leg_bye_runs ? true : false
          const isWide = wide_runs ? true : false
          const isNoBall = no_ball_runs ? true : false
          const isByes = byes_runs ? true : false
          const isPenalty = penalty_runs ? true : false

          const wicket_kind = delivery.wickets ? delivery.wickets[0].kind : null
          const is_wicket = delivery.wickets?.length ? true : false
          const player_out = delivery.wickets ? delivery.wickets[0].player_out : null

          // Extract fielder names
          const fielderNames = delivery.wickets?.flatMap(wicket => 
            wicket.fielders?.map(fielder => fielder.name)
          );

          const ball = {
            season_id: seasonId,
            match_id: matchId,
            batter: delivery.batter,
            bowler: delivery.bowler,
            non_striker: delivery.non_striker,
            team_batting,
            team_bowling,
            over_number,
            ball_number: index,
            batter_runs: delivery.runs.batter || 0,
            extras: delivery.runs.extras || 0,
            total_runs: delivery.runs.total || 0,
            batsman_type: batter.batStyle,
            bowler_type: bowler.bowlStyle || null,
            player_out: player_out,
            fielders_involved: fielderNames,
            is_wicket: is_wicket,
            is_wide_ball: isWide,
            is_no_ball: isNoBall,
            is_leg_bye: isLegBye,
            is_bye: isByes,
            is_penalty: isPenalty,
            wide_ball_runs: wide_runs,
            no_ball_runs: no_ball_runs,
            leg_bye_runs: leg_bye_runs,
            bye_runs: byes_runs,
            penalty_runs: penalty_runs,
            wicket_kind: wicket_kind,
            is_super_over: is_super_over,
            innings: inningsNum
          };
          
          console.log({ball})
          // await sleep(1000);
          try {
          await insertBallStat(ball);
          } catch (err) {
            console.error('Insert error:', err.message);
          }
        }
      }
    }
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
            const inningsData = jsonData.innings

            if(shouldProcessMatch(matchId)){
              await processBallByBallData(matchId, matchInfo, inningsData)
            }
        }
    }

}

main()