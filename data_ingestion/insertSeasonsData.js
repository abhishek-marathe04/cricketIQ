const pool = require('./db');
const fs = require('fs');
const path = require("path");


const filePath = path.join(__dirname, "dataset/seasons_data/seasons_data.json"); // Update with actual file name

const insertSeasons = async (seasons) => {
    const client = await pool.connect();
    try {
      for (const season of seasons) {
        // Get winner & runner-up team IDs
        const winnerRes = await client.query("SELECT team_id FROM team_aliases WHERE alias_name = $1", [season.winner]);
        const runnerUpRes = await client.query("SELECT team_id FROM team_aliases WHERE alias_name = $1", [season.runner_up]);
  
        if (winnerRes.rows.length === 0 || runnerUpRes.rows.length === 0) {
          console.log(`Skipping season ${season.year}: Teams not found`);
          // continue;
        }
  
        const winnerId = winnerRes.rows[0]?.team_id;
        const runnerUpId = runnerUpRes.rows[0]?.team_id;
  
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