const fs = require('fs');
const csv = require('csv-parser');

const processedMatchIds = new Set();

function loadProcessedMatchIds(csvPath) {
  return new Promise((resolve, reject) => {
    fs.createReadStream(csvPath)
      .pipe(csv())
      .on('data', (row) => {
        // Assuming column name is 'match_id' (adjust if needed)
        if (row.match_id) {
          processedMatchIds.add(parseInt(row.match_id));
        }
      })
      .on('end', () => {
        console.log('Processed match IDs loaded.');
        resolve();
      })
      .on('error', reject);
  });
}

function shouldProcessMatch(matchId) {
  return !processedMatchIds.has(matchId);
}

loadProcessedMatchIds('dataset/loaded_matches_data.csv')
module.exports = {
  shouldProcessMatch
};
