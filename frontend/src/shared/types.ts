/**
 * shared/types.ts
 * Shared Typescript interfaces and types.
 */

export type Player = {
    id: string;
    name: string;
    team: string;
    position: string;
    average?: number;
}