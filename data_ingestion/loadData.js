const pool = require('./db');
const fs = require('fs');

// Load JSON file
const jsonData = JSON.parse(fs.readFileSync('match_data.json', 'utf8'));

async function insertMatchData() {
  try {
    const query = `
      INSERT INTO matches (season_id, balls_per_over, city, match_date, event_name, match_number, gender, match_type, overs, team_type, venue, toss_winner, toss_decision, match_winner, win_by_runs, win_by_wickets, player_of_match)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
      RETURNING match_id;
    `;

    const values = [
      jsonData.season, // Replace with actual field mapping
      jsonData.balls_per_over,
      jsonData.city,
      jsonData.dates[0],
      jsonData.event.name,
      jsonData.event.match_number,
      jsonData.gender,
      jsonData.match_type,
      jsonData.overs,
      jsonData.team_type,
      jsonData.venue,
      jsonData.toss.winner,
      jsonData.toss.decision,
      jsonData.outcome.winner,
      jsonData.outcome.by?.runs || null,
      jsonData.outcome.by?.wickets || null,
      jsonData.player_of_match[0]
    ];

    const res = await pool.query(query, values);
    console.log('Inserted match with ID:', res.rows[0].match_id);
  } catch (error) {
    console.error('Error inserting data:', error);
  } finally {
    pool.end();
  }
}

insertMatchData();
