const pool = require('./db');

async function insertTeamAlias(teamName, aliasName) {
    const client = await pool.connect();
    try {
      // Step 1: Get team_id from official_name
      const teamResult = await client.query(
        "SELECT team_id FROM teams WHERE team_name = $1",
        [teamName]
      );
  
      if (teamResult.rows.length === 0) {
        throw new Error(`No official team found for: ${teamName}`);
      }
  
      const teamId = teamResult.rows[0].team_id;
  
      // Step 2: Insert alias
      await client.query(
        "INSERT INTO team_aliases (team_id, alias_name) VALUES ($1, $2) ON CONFLICT (alias_name) DO NOTHING",
        [teamId, aliasName]
      );
  
      console.log(`Alias '${aliasName}' added for team '${teamName}'`);
    } catch (error) {
      console.error("Error inserting alias:", error.message);
    } finally {
      client.release();
    }
  }
  
  async function main() {
    await insertTeamAlias("Royal Challengers Bangalore", "RCB");
    await insertTeamAlias("Royal Challengers Bangalore", "Royal Challengers Bengaluru");
    await insertTeamAlias("Delhi Capitals", "Delhi Daredevils");
    await insertTeamAlias("Punjab Kings", "Kings XI Punjab");
    await insertTeamAlias("Royal Challengers Bangalore", "Royal Challengers Bangalore");
    await insertTeamAlias("Royal Challengers Bangalore", "Banglore");
    await insertTeamAlias("Royal Challengers Bangalore", "Bengaluru");
    await insertTeamAlias("Delhi Capitals", "Delhi Capitals");
    await insertTeamAlias("Delhi Capitals", "DC");
    await insertTeamAlias("Delhi Capitals", "DD");
    await insertTeamAlias("Delhi Capitals", "Delhi");
    await insertTeamAlias("Punjab Kings", "Punjab Kings");
    await insertTeamAlias("Punjab Kings", "KXIP");
    await insertTeamAlias("Punjab Kings", "Punjab");
    await insertTeamAlias("Sunrisers Hyderabad", "Sunrisers Hyderabad");
    await insertTeamAlias("Sunrisers Hyderabad", "SRH");
    await insertTeamAlias("Sunrisers Hyderabad", "Hyderabad");
    await insertTeamAlias("Sunrisers Hyderabad", "Deccan Chargers");
    await insertTeamAlias("Mumbai Indians", "Mumbai Indians");
    await insertTeamAlias("Mumbai Indians", "MI");
    await insertTeamAlias("Mumbai Indians", "Mumbai");
    await insertTeamAlias("Rising Pune Supergiant", "Rising Pune Supergiant");
    await insertTeamAlias("Rising Pune Supergiant", "Rising Pune Supergiants");
    await insertTeamAlias("Rising Pune Supergiant", "RPS");
    await insertTeamAlias("Rising Pune Supergiant", "Pune");
    await insertTeamAlias("Gujarat Lions", "Gujarat Lions");
    await insertTeamAlias("Gujarat Lions", "GL");
    await insertTeamAlias("Kolkata Knight Riders", "Kolkata Knight Riders");
    await insertTeamAlias("Kolkata Knight Riders", "KKR");
    await insertTeamAlias("Kolkata Knight Riders", "Kolkatta");
    await insertTeamAlias("Chennai Super Kings", "Chennai Super Kings");
    await insertTeamAlias("Chennai Super Kings", "CSK");
    await insertTeamAlias("Chennai Super Kings", "Chennai");
    await insertTeamAlias("Rajasthan Royals", "Rajasthan Royals");
    await insertTeamAlias("Rajasthan Royals", "Rajasthan");
    await insertTeamAlias("Rajasthan Royals", "RR");
    await insertTeamAlias("Lucknow Super Giants", "Lucknow Super Giants");
    await insertTeamAlias("Lucknow Super Giants", "LSG");
    await insertTeamAlias("Lucknow Super Giants", "Lucknow");
    await insertTeamAlias("Gujarat Titans", "Gujarat Titans");
    await insertTeamAlias("Gujarat Titans", "GT");
    await insertTeamAlias("Kochi Tuskers Kerala", "Kochi Tuskers Kerala");
    await insertTeamAlias("Kochi Tuskers Kerala", "KTK");
    await insertTeamAlias("Kochi Tuskers Kerala", "Kerala");
    await insertTeamAlias("Pune Warriors", "Pune Warriors");
    await insertTeamAlias("Pune Warriors", "PWI");
  }

main()