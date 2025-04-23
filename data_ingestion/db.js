const { Pool } = require('pg');

const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'cricketiq',
  password: 'postgres_cric',
  port: 5432, // Default PostgreSQL port
});

module.exports = pool;
