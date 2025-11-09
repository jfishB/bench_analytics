/**
 * shared/api.ts
 * Simple wrapper around fetch for consistent API requests.
 */

const BASE_URL = "https://api.example.com"; // Replace with actual API base URL

/** 
 * Generic request wrapper.
 * @param endpoint - API endpoint (without base URL)
 * @param options - Fetch options (method, headers, body)
 */
export async function apiRequest(endpoint: string, options: RequestInit = {}){
    const response  = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || 'API request failed');
  }

  return response.json();   
}