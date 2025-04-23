-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: PostgreSQL
-- Generated at: 2025-04-12T08:52:45.793Z

CREATE TABLE "seasons" (
  "season_id" serial PRIMARY KEY,
  "year" integer UNIQUE NOT NULL,
  "start_date" date,
  "end_date" date,
  "winner" integer,
  "runner_up" integer
);

CREATE TABLE "matches" (
  "match_id" serial PRIMARY KEY,
  "season_id" integer,
  "balls_per_over" integer,
  "city" varchar(100),
  "match_date" date,
  "event_name" varchar(100),
  "match_number" integer,
  "gender" varchar(10),
  "match_type" varchar(20),
  "format" varchar(20),
  "overs" integer,
  "season" varchar(10),
  "team_type" varchar(20),
  "venue" varchar(255),
  "toss_winner" integer,
  "team1" integer,
  "team2" integer,
  "toss_decision" varchar(10),
  "match_winner" integer,
  "win_by_runs" integer,
  "win_by_wickets" integer,
  "result" varchar(10) DEFAULT 'win',
  "player_of_match" integer
);

CREATE TABLE "team_performance" (
  "performance_id" serial PRIMARY KEY,
  "match_id" integer,
  "team_id" integer,
  "opponent_team_id" integer,
  "total_runs" integer,
  "wickets_lost" integer,
  "overs_faced" decimal(3,1),
  "extras" integer,
  "boundaries" integer,
  "sixes" integer,
  "run_rate" decimal(4,2),
  "result" varchar(10)
);

CREATE TABLE "players" (
  "player_id" serial PRIMARY KEY,
  "player_name" varchar(100) UNIQUE NOT NULL,
  "bat_style" varchar(50),
  "bowl_style" varchar(50),
  "field_pos" varchar(50),
  "player_full_name" varchar(100)
);

CREATE TABLE "teams" (
  "team_id" serial PRIMARY KEY,
  "team_name" varchar(100) UNIQUE NOT NULL
);

CREATE TABLE "team_aliases" (
  "alias_id" serial PRIMARY KEY,
  "team_id" integer,
  "alias_name" varchar(100) UNIQUE NOT NULL
);

CREATE TABLE "player_performance" (
  "performance_id" serial PRIMARY KEY,
  "match_id" integer,
  "player_id" integer,
  "player_name" varchar,
  "runs_scored" integer,
  "balls_faced" integer,
  "fours" integer,
  "sixes" integer,
  "wickets_taken" integer,
  "overs_bowled" decimal(3,1),
  "extras_conceded" integer,
  "dot_balls_bowled" integer,
  "maidens" integer,
  "runs_conceded" integer,
  "catches" integer,
  "stumpings" integer,
  "run_outs" integer,
  "team_id" integer,
  "team_name" varchar,
  "opponent_team_id" integer,
  "opponent_team_name" varchar
);

CREATE TABLE "ball_by_ball_stats" (
  "season_id" integer,
  "match_id" integer,
  "batter" varchar,
  "bowler" varchar,
  "non_striker" varchar,
  "team_batting" integer,
  "team_bowling" integer,
  "over_number" integer,
  "ball_number" integer,
  "batter_runs" integer,
  "extras" integer,
  "total_runs" integer,
  "batsman_type" varchar(100),
  "bowler_type" varchar(100),
  "player_out" varchar(100),
  "fielders_involved" JSON,
  "is_wicket" bool DEFAULT false,
  "is_wide_ball" bool DEFAULT false,
  "is_no_ball" bool DEFAULT false,
  "is_leg_bye" bool DEFAULT false,
  "is_bye" bool DEFAULT false,
  "is_penalty" bool DEFAULT false,
  "wide_ball_runs" integer DEFAULT 0,
  "no_ball_runs" integer DEFAULT 0,
  "leg_bye_runs" integer DEFAULT 0,
  "bye_runs" integer DEFAULT 0,
  "penalty_runs" integer DEFAULT 0,
  "wicket_kind" varchar(100),
  "is_super_over" bool DEFAULT false,
  "innings" integer
);

CREATE UNIQUE INDEX ON "player_performance" ("match_id", "player_id");

CREATE UNIQUE INDEX ON "ball_by_ball_stats" ("match_id", "innings", "over_number", "ball_number");

ALTER TABLE "seasons" ADD FOREIGN KEY ("winner") REFERENCES "teams" ("team_id");

ALTER TABLE "seasons" ADD FOREIGN KEY ("runner_up") REFERENCES "teams" ("team_id");

ALTER TABLE "matches" ADD FOREIGN KEY ("season_id") REFERENCES "seasons" ("season_id");

ALTER TABLE "matches" ADD FOREIGN KEY ("toss_winner") REFERENCES "teams" ("team_id");

ALTER TABLE "matches" ADD FOREIGN KEY ("team1") REFERENCES "teams" ("team_id");

ALTER TABLE "matches" ADD FOREIGN KEY ("team2") REFERENCES "teams" ("team_id");

ALTER TABLE "matches" ADD FOREIGN KEY ("match_winner") REFERENCES "teams" ("team_id");

ALTER TABLE "matches" ADD FOREIGN KEY ("player_of_match") REFERENCES "players" ("player_id");

ALTER TABLE "team_performance" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("match_id");

ALTER TABLE "team_performance" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("team_id");

ALTER TABLE "team_performance" ADD FOREIGN KEY ("opponent_team_id") REFERENCES "teams" ("team_id");

ALTER TABLE "team_aliases" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("team_id");

ALTER TABLE "player_performance" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("match_id");

ALTER TABLE "player_performance" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("player_id");

ALTER TABLE "player_performance" ADD FOREIGN KEY ("player_name") REFERENCES "players" ("player_name");

ALTER TABLE "player_performance" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("team_id");

ALTER TABLE "player_performance" ADD FOREIGN KEY ("team_name") REFERENCES "teams" ("team_name");

ALTER TABLE "player_performance" ADD FOREIGN KEY ("opponent_team_id") REFERENCES "teams" ("team_id");

ALTER TABLE "player_performance" ADD FOREIGN KEY ("opponent_team_name") REFERENCES "teams" ("team_name");

ALTER TABLE "ball_by_ball_stats" ADD FOREIGN KEY ("season_id") REFERENCES "seasons" ("season_id");

ALTER TABLE "ball_by_ball_stats" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("match_id");

ALTER TABLE "ball_by_ball_stats" ADD FOREIGN KEY ("batter") REFERENCES "players" ("player_name");

ALTER TABLE "ball_by_ball_stats" ADD FOREIGN KEY ("bowler") REFERENCES "players" ("player_name");

ALTER TABLE "ball_by_ball_stats" ADD FOREIGN KEY ("non_striker") REFERENCES "players" ("player_name");

ALTER TABLE "ball_by_ball_stats" ADD FOREIGN KEY ("team_batting") REFERENCES "teams" ("team_id");

ALTER TABLE "ball_by_ball_stats" ADD FOREIGN KEY ("team_bowling") REFERENCES "teams" ("team_id");
