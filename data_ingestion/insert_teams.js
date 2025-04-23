const { Client } = require("pg");
const fs = require('fs');
const path = require("path");

const client = new Client({
  user: 'postgres',
  host: 'localhost',
  database: 'cricketiq',
  password: 'postgres_cric',
  port: 5432, // Default PostgreSQL port
});


async function insertTeam(teamName) {
    // Step 1: Check if the team name exists in team_aliases
    const aliasRes = await client.query(
      "SELECT team_id FROM team_aliases WHERE alias_name = $1",
      [teamName]
    );
  
    let teamId;
    if (aliasRes.rows.length > 0) {
        console.log(`Found Team : ${teamName} already exists id ${teamId}`)
      teamId = aliasRes.rows[0].team_id; // Use the mapped team_id
    } else {
      // Step 2: If not found in aliases, check in teams table
      const teamRes = await client.query(
        "INSERT INTO teams (team_name) VALUES ($1) ON CONFLICT (team_name) DO NOTHING RETURNING team_id",
        [teamName]
      );
  
      teamId = teamRes.rows.length ? teamRes.rows[0].team_id : null;
  
      // Step 3: If a new team was added, insert the alias as well
      if (teamId) {
        await client.query(
          "INSERT INTO team_aliases (team_id, alias_name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
          [teamId, teamName]
        );
      }
      console.log(` Team : ${teamName} added successfully with id ${teamId}`)
    }
  
    return teamId;
  }

// Add new team
insertTeam("");