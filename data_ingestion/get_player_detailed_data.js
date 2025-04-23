const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const pool = require('./db');

const filePath = path.join(__dirname, "dataset/player_data/player_profile.csv"); // Update with actual file name

const playersData = [];

async function updatePlayer(player) {
    const client = await pool.connect();
    try {
      // ✅ Update player details where name matches
      const query = `
        UPDATE players 
        SET bat_style = $1, bowl_style = $2, field_pos = $3, player_full_name = $4
        WHERE player_name = $5
      `;
      
      const values = [
        player.bat_style || null,
        player.bowl_style || null,
        player.field_pos || null,
        player.full_name || null,
        player.name,
      ];
  
      const res = await client.query(query, values);
      if (res.rowCount > 0) {
        console.log(`✅ Updated player: ${player.name}`);
      } else {
        console.log(`⚠️ No player found with name: ${player.name}`);
      }
    } catch (error) {
      console.error("❌ Error updating player:", error.message);
    } finally {
      client.release();
    }
  }

fs.createReadStream(filePath)
  .pipe(csv())
  .on("data", async (row) => {
    const player = {
      name: row.unique_name,
      full_name: row.name,
      bat_style: row.bat_style,
      bowl_style: row.bowl_style,
      field_pos: row.field_pos || "N/A", // Handle missing field_pos
    };
    console.log({player})
    // playersData.push(player);
    await updatePlayer(player);
  })
  .on("end", () => {
    console.log("All Players Data Updated");
  })
  .on("error", (err) => {
    console.error("Error reading CSV:", err);
  });
