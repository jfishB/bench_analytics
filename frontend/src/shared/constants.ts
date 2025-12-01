/**
 * Application-wide constants and configuration values
 */

export const SIMULATION_CONFIG = {
  DEFAULT_NUM_GAMES: 20000,
  MIN_GAMES: 100,
  MAX_GAMES: 100000,
  LINEUP_SIZE: 9,
  STATUS_MESSAGE_INTERVAL: 800, // milliseconds
  STEP_SIZE: 100,
} as const;

export const STATUS_MESSAGES = [
  "Simulating your lineups...",
  "Calculating runs...",
  "Tracking base runners...",
  "Recording outcomes...",
  "Running Monte Carlo iterations...",
  "Processing game states...",
  "Evaluating batting sequences...",
  "Analyzing scoring patterns...",
  "Computing probabilities...",
  "Comparing results...",
  "Aggregating statistics...",
] as const;

export const UI_MESSAGES = {
  NO_LINEUPS: {
    TITLE: "No Saved Lineups Yet",
    DESCRIPTION: "Create and save lineups in the Generate Lineup tab to see them here.",
  },
  SELECT_PLAYERS: {
    TITLE: "Select 9 Players From Your Roster First",
    DESCRIPTION:
      'Go to the Current Roster tab, select 9 players using the checkboxes, then click "Create Lineup".',
  },
  DELETE_CONFIRMATION: "Are you sure you want to delete this lineup?",
  LOADING: "Loading lineups...",
  INITIALIZING: "Initializing simulation...",
} as const;
