const { Client } = require("pg");
const fs = require('fs');
const path = require("path");
const { shouldProcessMatch } = require("./matchFilter");

const client = new Client({
  user: 'postgres',
  host: 'localhost',
  database: 'cricketiq',
  password: 'postgres_cric',
  port: 5432, // Default PostgreSQL port
});

// Folder containing JSON files
const DATA_FOLDER = "./dataset/matches_data"; // Update with the actual folder path

async function processFiles() {
  await client.connect();

  try {
    const files = fs.readdirSync(DATA_FOLDER); // Get all files in the folder

    for (const file of files) {
      if (path.extname(file) === ".json") {
        console.log(`Processing file: ${file}`);

        const filePath = path.join(DATA_FOLDER, file);
        const jsonData = JSON.parse(fs.readFileSync(filePath, "utf8"));
        const matchId = parseInt(path.basename(file, '.json'), 10);
        if (shouldProcessMatch(matchId)){
          await insertPlayers(jsonData.info.players);
        }
      }
    }

    console.log("✅ All files processed successfully!");
  } catch (error) {
    console.error("❌ Error processing files:", error);
  } finally {
    await client.end();
  }
}

async function insertPlayers(playersData) {
  for (const [teamName, players] of Object.entries(playersData)) {

    for (const playerName of players) {
      // Insert player
      const playerRes = await client.query(
        "INSERT INTO players (player_name) VALUES ($1) ON CONFLICT (player_name) DO NOTHING RETURNING player_id",
        [playerName]
      );
      const playerId = playerRes.rows.length ? playerRes.rows[0].player_id : null;

      console.log(` Player : ${playerName} added successfully with id ${playerId}`)
    }
  }
}

// Start processing
processFiles();