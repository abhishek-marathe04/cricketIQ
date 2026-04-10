const pool = require('./db');
const fs = require('fs');
const path = require("path");


const filePath = path.join(__dirname, "dataset/seasons_data/seasons_data.json"); // Update with actual file name

const insertSeasons = async (seasons) => {
    const client = await pool.connect();
    try {
      for (const season of seasons) {
        // Get winner & runner-up team IDs
        const winnerRes = season.winner
          ? await client.query("SELECT team_id FROM team_aliases WHERE alias_name = $1", [season.winner])
          : { rows: [] };
        const runnerUpRes = season.runner_up
          ? await client.query("SELECT team_id FROM team_aliases WHERE alias_name = $1", [season.runner_up])
          : { rows: [] };

        if (season.winner && winnerRes.rows.length === 0) {
          console.log(`Warning: winner team "${season.winner}" not found for season ${season.year}, inserting with null winner`);
        }
        if (season.runner_up && runnerUpRes.rows.length === 0) {
          console.log(`Warning: runner-up team "${season.runner_up}" not found for season ${season.year}, inserting with null runner_up`);
        }

        const winnerId = winnerRes.rows[0]?.team_id ?? null;
        const runnerUpId = runnerUpRes.rows[0]?.team_id ?? null;

        await client.query(
          `INSERT INTO seasons (season_id, year, start_date, end_date, winner, runner_up)
           VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (year) DO NOTHING`,
          [season.year, season.year, season.start_date, season.end_date, winnerId, runnerUpId]
        );
      }
      console.log("Seasons data inserted successfully!");
    } catch (err) {
      console.error("Error inserting seasons data:", err);
    } finally {
      client.release();
    }
  };
  
  async function main(){
      const jsonData = JSON.parse(fs.readFileSync(filePath, "utf8"));

      console.log({jsonData})
      insertSeasons(jsonData);
  }
  
  main()