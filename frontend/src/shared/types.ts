/**
 * Centralized TypeScript interfaces and type definitions shared across the app.
 */

export type Player = {
    // Unique player identifier
    id: string;

    // Full name of the player
    name: string;

    // Team the player belongs to
    team: string;

    // Player's position on the field
    position: string;

    // Batting average (optional)
    average?: number;
}